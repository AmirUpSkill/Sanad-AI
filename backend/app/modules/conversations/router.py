import math
import uuid
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db, get_current_user, CurrentUser
from app.modules.conversations.models import ConversationStatus
from app.modules.conversations.schemas import (
    ConversationCreate,
    ConversationUpdate,
    ConversationOut,
    ConversationListResponse,
    Pagination,
)
from app.modules.conversations.service import ConversationsService

router = APIRouter(prefix="/conversations", tags=["conversations"])
service = ConversationsService()


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    status_filter: ConversationStatus | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
) -> ConversationListResponse:
    items, total_items = await service.list_conversations(
        db,
        owner_id=user.id,
        page=page,
        limit=limit,
        status_filter=status_filter,
    )

    total_pages = max(1, math.ceil(total_items / limit)) if limit else 1
    pagination = Pagination(
        page=page,
        limit=limit,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )
    return ConversationListResponse(
        data=[ConversationOut.model_validate(x) for x in items],
        pagination=pagination,
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ConversationOut)
async def create_conversation(
    payload: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
) -> ConversationOut:
    conv = await service.create_conversation(db, owner_id=user.id, payload=payload)
    return ConversationOut.model_validate(conv)


@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
) -> ConversationOut:
    conv = await service.get_conversation(db, owner_id=user.id, conversation_id=conversation_id)
    return ConversationOut.model_validate(conv)


@router.patch("/{conversation_id}", response_model=ConversationOut)
async def update_conversation(
    conversation_id: uuid.UUID,
    payload: ConversationUpdate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
) -> ConversationOut:
    conv = await service.update_conversation(
        db,
        owner_id=user.id,
        conversation_id=conversation_id,
        payload=payload,
    )
    return ConversationOut.model_validate(conv)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
) -> Response:
    await service.delete_conversation(db, owner_id=user.id, conversation_id=conversation_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)