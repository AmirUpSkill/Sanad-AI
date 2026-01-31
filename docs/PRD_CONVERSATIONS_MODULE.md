# PRD — Conversations Module

## 1) Overview
The Conversations module is the first domain module of SanadAI. It provides the core primitives to create, update, list, and archive conversation records that will later be used to store user interactions, document summaries, and AI-generated responses.

This PRD defines the API surface, data model, service boundaries, repository responsibilities, and testing expectations so any engineer can implement it consistently.

## 2) Goals
- Provide a consistent, versioned REST API for conversation lifecycle management.
- Persist conversations with minimal required fields and extensible metadata.
- Ensure clean separation of concerns (router → service → repository → database).
- Support multi-user ownership and basic access control hooks.
- Be testable with unit and integration tests.

## 3) Non-Goals
- Message storage and streaming response handling (future module).
- Real-time collaboration (future).
- Advanced permissions/roles beyond ownership (future).
- Full-text search (future).

## 4) Personas and User Stories
### Primary user
- Authenticated user using the product to create and manage conversations.

### Stories
- As a user, I can create a new conversation and optionally give it a title.
- As a user, I can list my conversations with pagination and sorting.
- As a user, I can retrieve a conversation by ID.
- As a user, I can update the title or status of a conversation.
- As a user, I can archive or delete a conversation.

## 5) Functional Requirements
### 5.1 Conversations CRUD
- Create conversation with optional title and metadata.
- Retrieve by ID with ownership enforcement.
- List with pagination, filtering by status, and sorting by updated_at.
- Update title and status.
- Soft delete (archived_at) with optional hard delete for admin/internal.

### 5.2 Ownership & Access Control
- Each conversation belongs to a single user (`owner_id`).
- All reads/writes are scoped to the requesting user.
- If ownership fails, return 404 (do not leak existence).

### 5.3 Metadata
- Store JSON metadata for extensibility (e.g., language, channel, tags).
- Metadata is optional and should be validated as a dictionary.

### 5.4 Status
- `status` is an enum: `active`, `archived`, `deleted`.
- Default is `active`.
- Only transitions allowed: `active -> archived`, `archived -> active`, `active/archived -> deleted`.

## 6) Data Model
### 6.1 Conversation Model (database)
Table: `conversations`

Fields:
- `id` (UUID, primary key)
- `owner_id` (UUID, indexed)
- `title` (string, nullable, length 255)
- `status` (enum: active, archived, deleted)
- `metadata` (JSONB, nullable)
- `created_at` (timestamp, default now)
- `updated_at` (timestamp, auto update)
- `archived_at` (timestamp, nullable)
- `deleted_at` (timestamp, nullable)

Indexes:
- (`owner_id`, `updated_at` DESC)
- (`owner_id`, `status`)

Constraints:
- `title` trimmed; if empty string, set to null.

### 6.2 Domain Model (Pydantic / Schemas)
- `ConversationCreate` — title?, metadata?
- `ConversationUpdate` — title?, status?
- `ConversationOut` — id, owner_id, title, status, metadata, created_at, updated_at, archived_at
- `ConversationList` — items: list[ConversationOut], page, page_size, total

## 7) API Specification
Base path: `/api/v1/conversations`

### 7.1 Create
`POST /api/v1/conversations`
Request:
```
{
  "title": "Case A",
  "metadata": {"language": "en"}
}
```
Response: `201 Created` with `ConversationOut`.

### 7.2 List
`GET /api/v1/conversations?page=1&page_size=20&status=active&sort=updated_at_desc`
Response: `200 OK` with `ConversationList`.

### 7.3 Get by ID
`GET /api/v1/conversations/{conversation_id}`
Response: `200 OK` with `ConversationOut` or `404`.

### 7.4 Update
`PATCH /api/v1/conversations/{conversation_id}`
Request:
```
{
  "title": "New title",
  "status": "archived"
}
```
Response: `200 OK` with `ConversationOut`.

### 7.5 Delete (soft)
`DELETE /api/v1/conversations/{conversation_id}`
Response: `204 No Content` (sets `status=deleted`, `deleted_at`).

### 7.6 Errors
Standard error response:
```
{
  "error": {
    "code": "HTTP_ERROR",
    "message": "Not Found",
    "details": null
  }
}
```
Use existing core exception handlers.

## 8) Service Layer Responsibilities
- Validate business rules and transitions.
- Normalize input (trim title, empty -> null).
- Enforce ownership via repository queries.
- Convert repository results to schemas.

## 9) Repository Layer Responsibilities
- Encapsulate database access (async SQLAlchemy).
- Provide methods:
  - `create(owner_id, data)`
  - `get_by_id(owner_id, id)`
  - `list(owner_id, filters, pagination, sorting)`
  - `update(owner_id, id, data)`
  - `soft_delete(owner_id, id)`

## 10) Router Responsibilities
- Define FastAPI routes for CRUD operations.
- Inject dependencies: db session, current user.
- Return schema responses.

## 11) Security & Auth
- All routes require authentication (placeholder dependency: `get_current_user`).
- Must not expose other users' conversations.

## 12) Observability
- Log creation/update/delete events at INFO level.
- Include `conversation_id` and `owner_id` in logs.

## 13) Testing Requirements
### Unit Tests
- Title normalization.
- Status transitions (valid/invalid).
- Service-level errors.

### Integration Tests
- Create/list/get/update/delete flow with a test DB.
- Ownership isolation (user A cannot access user B’s conversations).

## 14) Migration Plan
- Create Alembic migration for `conversations` table.
- Add enum type for status if DB supports it.

## 15) Future Extensions
- Messages module with conversation_id foreign key.
- Search and filters on metadata.
- Shared conversations and permissions.
- Tags and folders.

## 16) Open Questions
- What is the source of `owner_id` (auth provider)?
- Should delete be hard delete for free-tier cleanup?
- Do we need a default auto-title strategy?
