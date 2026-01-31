import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# --- We Import the need Models , Repositories , Schemas --- 
from app.modules.conversations.models import Conversation, ConversationStatus
from app.modules.conversations.repository import ConversationsRepository
from app.modules.conversations.schemas import ConversationCreate, ConversationUpdate

class ConversationsService:
    def __init__(self, repo: ConversationsRepository | None = None ) -> None:
        self.repo = repo or ConversationsRepository()
    
    async def create_conversation(
        self,
        db: AsyncSession,
        *,
        owner_id: uuid.UUID,
        payload: ConversationCreate,
    ) -> Conversation:
        return await self.repo.create(
            db,
            owner_id=owner_id,
            title=payload.title,
            metadata=payload.metadata,

        )
    async def get_conversation(
        self,
        db: AsyncSession,
        *,
        owner_id: uuid.UUID,
        conversation_id: uuid.UUID
    ) -> Conversation:
        conv = await self.repo.get_by_id(db, owner_id=owner_id,conversation_id=conversation_id)
        if not conv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Conversation  not found ")
        return conv 
    async def list_conversations(
        self,
        db: AsyncSession,
        *,
        owner_id: uuid.UUID,
        page: int,
        limit: int, 
        status_filter: ConversationStatus | None,
    ) -> tuple[list[Conversation],int]:
        return await self.repo.list(
            db,
            owner_id=owner_id,
            page=page,
            limit=limit,
            status=status_filter,
        )
    def _apply_status_transition(self, conv: Conversation, new_status: ConversationStatus) -> None:
        # --- Do not Allow Change when been deleted --- 
        if conv.status == ConversationStatus.deleted:
            raise HTTPException(status_code=409, detail="Conversation is deleted and connot be modified")
        now = datetime.now(timezone.utc)
        if new_status == ConversationStatus.archived:
            if conv.status == ConversationStatus.active:
                conv.status = ConversationStatus.archived
                conv.archived_at = now
                return
            if conv.status == ConversationStatus.archived:
                return  # --- idempotent ---
            raise HTTPException(status_code=409, detail="Invalid status transition")

        if new_status == ConversationStatus.active:
            if conv.status == ConversationStatus.archived:
                conv.status = ConversationStatus.active
                conv.archived_at = None
                return
            if conv.status == ConversationStatus.active:
                return  # --- idempotent ---
            raise HTTPException(status_code=409, detail="Invalid status transition")

        if new_status == ConversationStatus.deleted:
            conv.status = ConversationStatus.deleted
            conv.deleted_at = now
            return

        raise HTTPException(status_code=409, detail="Invalid status transition")
    async def update_conversation(
        self,
        db: AsyncSession,
        *,
        owner_id: uuid.UUID,
        conversation_id: uuid.UUID,
        payload: ConversationUpdate
    ) -> Conversation:
        conv = await self.get_conversation(db, owner_id=owner_id, conversation_id=conversation_id)
        update_fields: dict[str, object] = {}

        # --- Apply Title update ---
        if "title" in payload.model_fields_set:
            conv.title = payload.title
            update_fields["title"] = conv.title

        # --- Apply metadata update ---
        if "metadata" in payload.model_fields_set:
            conv.metadata_ = payload.metadata
            update_fields["metadata"] = conv.metadata_

        # --- Apply Status transition rules ---
        if "status" in payload.model_fields_set and payload.status is not None:
            self._apply_status_transition(conv, payload.status)
            update_fields["status"] = conv.status

        # --- Let's Persist via repo ---
        return await self.repo.update(db, conversation=conv, **update_fields)
    async def delete_conversation(
        self,
        db: AsyncSession,
        *,
        owner_id: uuid.UUID,
        conversation_id: uuid.UUID,
        ) -> None:
        conv = await self.get_conversation(db, owner_id=owner_id, conversation_id=conversation_id)
        self._apply_status_transition(conv, ConversationStatus.deleted)
        await self.repo.update(db, conversation=conv, status=conv.status)
