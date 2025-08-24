from fastapi import FastAPI, Header

from app.middlewares import ErrorHandlingMiddleware, LoggingMiddleware
from app.routes import healthcheck, signin, user
from app.schemas import header_schema

app = FastAPI()
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.include_router(healthcheck.router)
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
