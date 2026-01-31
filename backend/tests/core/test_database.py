from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker


def test_session_factory_creates_session_without_connecting():
    async def _run() -> None:
        session = async_session_maker()
        assert isinstance(session, AsyncSession)
        await session.close()

    import asyncio

    asyncio.run(_run())
