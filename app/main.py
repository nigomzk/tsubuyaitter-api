from fastapi import FastAPI

from app.routes import auth

app = FastAPI()
app.include_router(auth.router)


@app.get("/")
async def root():
    """
    テストAPI

    Returns:
        dict[str, str]: メッセージ
    """
    return {'message": "Hello World'}
