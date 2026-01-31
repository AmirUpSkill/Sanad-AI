from fastapi import APIRouter

from app.modules.conversations.router import router as conversations_router

api_router = APIRouter()

api_router.include_router(conversations_router)
