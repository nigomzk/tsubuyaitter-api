from fastapi import FastAPI, Header

from app.middlewares import LoggingMiddleware
from app.routes import health_check, signin, user
from app.schemas import header_schema

app = FastAPI()
app.add_middleware(LoggingMiddleware)
app.include_router(health_check.router)
app.include_router(signin.router)
app.include_router(user.router)


@app.get("/")
async def root(header: header_schema.CommonHeders = Header()):
    """
    テストAPI

    Returns:
        dict[str, str]: メッセージ
    """
    return {"message": "Hello World"}
