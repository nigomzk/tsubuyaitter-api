from fastapi import FastAPI

from app.routes import health_check, user

app = FastAPI()
app.include_router(health_check.router)
app.include_router(user.router)


@app.get("/")
async def root():
    """
    テストAPI

    Returns:
        dict[str, str]: メッセージ
    """
    return {'message": "Hello World'}
