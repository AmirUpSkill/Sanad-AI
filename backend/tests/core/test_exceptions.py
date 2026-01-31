import asyncio

from fastapi import FastAPI
from fastapi import Request

from app.core.exceptions import AppException, register_exception_handlers


def test_app_exception_returns_contract_shape():
    app = FastAPI()
    register_exception_handlers(app)

    handler = app.exception_handlers[AppException]
    request = Request({"type": "http", "method": "GET", "path": "/boom", "headers": []})

    async def _run():
        response = await handler(request, AppException(code="TEST_ERROR", message="Boom", status_code=418))
        assert response.status_code == 418
        payload = response.body.decode("utf-8")
        assert '"code":"TEST_ERROR"' in payload
        assert '"message":"Boom"' in payload

    asyncio.run(_run())
