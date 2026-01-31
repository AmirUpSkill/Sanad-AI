from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

from fastapi import Header
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session


class CurrentUser(BaseModel):
    id: uuid.UUID


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_async_session():
        yield session


async def get_current_user(x_user_id: str | None = Header(default=None)) -> CurrentUser:
    # Temporary stub for testing/front-end wiring. Replace with real auth later.
    if x_user_id:
        return CurrentUser(id=uuid.UUID(x_user_id))
    return CurrentUser(id=uuid.UUID("00000000-0000-0000-0000-000000000001"))
