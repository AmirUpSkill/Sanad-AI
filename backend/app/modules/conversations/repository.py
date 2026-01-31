# --- Standard Library Imports ---
import uuid

# --- Third-Party Imports ---
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

# --- Local Imports ---
from app.modules.conversations.models import Conversation, ConversationStatus

UNSET = object()


# --- Conversations Repository Class ---
class ConversationsRepository:
    """
        Repository for managing Conversation entities in the database.
    """

    # --- CREATE Operation ---
    async def create(
        self,
        db: AsyncSession,
        *,
        owner_id: uuid.UUID,
        title: str | None,
        metadata: dict | None,
    ) -> Conversation:
        """
            Create a new conversation in the database.
        """
        conv = Conversation(owner_id=owner_id, title=title, metadata_=metadata)
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        return conv

    # --- READ Operation: Get Single Conversation ---
    async def get_by_id(
        self,
        db: AsyncSession,
        *,
        owner_id: uuid.UUID,
        conversation_id: uuid.UUID,
        include_deleted: bool = False,
    ) -> Conversation | None:
        """
        Retrieve a conversation by its ID.
        Optionally include soft-deleted conversations.
        """
        # --- Build base query with owner and ID filters ---
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.owner_id == owner_id,
        )

        # --- Exclude deleted conversations unless explicitly requested ---
        if not include_deleted:
            stmt = stmt.where(Conversation.status != ConversationStatus.deleted)

        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    # --- READ Operation: List Conversations with Pagination ---
    async def list(
        self,
        db: AsyncSession,
        *,
        owner_id: uuid.UUID,
        page: int,
        limit: int,
        status: ConversationStatus | None,
    ) -> tuple[list[Conversation], int]:
        """
        List conversations for a user with pagination support.
        Returns a tuple of (conversations_list, total_count).
        """
        # --- Build base query filtered by owner ---
        base = select(Conversation).where(Conversation.owner_id == owner_id)

        # --- Apply status filter ---
        # Default behavior: do not show deleted unless explicitly asked
        if status is None:
            base = base.where(Conversation.status != ConversationStatus.deleted)
        else:
            base = base.where(Conversation.status == status)

        # --- Calculate total count for pagination metadata ---
        count_stmt = select(func.count()).select_from(base.subquery())
        total_items = int((await db.execute(count_stmt)).scalar_one())

        # --- Apply ordering and pagination ---
        stmt = (
            base.order_by(Conversation.updated_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = (await db.execute(stmt)).scalars().all()

        return items, total_items

    # --- UPDATE Operation ---
    async def update(
        self,
        db: AsyncSession,
        *,
        conversation: Conversation,
        title: str | None | object = UNSET,
        status: ConversationStatus | None | object = UNSET,
        metadata: dict | None | object = UNSET,
    ) -> Conversation:
        """
        Update conversation fields.
        Uses sentinel object() to distinguish between 'not provided' and 'set to None'.
        """
        # --- Apply field updates only if provided ---
        if title is not UNSET:
            conversation.title = title
        if status is not UNSET:
            conversation.status = status
        if metadata is not UNSET:
            conversation.metadata_ = metadata

        # --- Persist changes ---
        await db.commit()
        await db.refresh(conversation)
        return conversation

    # --- DELETE Operation: Soft Delete ---
    async def soft_delete(
        self,
        db: AsyncSession,
        *,
        conversation: Conversation,
    ) -> None:
        """
        Soft delete a conversation.
        Sets the status to 'deleted' without removing the record.
        """
        conversation.soft_delete()
        await db.commit()
