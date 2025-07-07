from fastapi import FastAPI

from app.routes import auth, helth_check

app = FastAPI()
app.include_router(auth.router)
app.include_router(helth_check.router)


@app.get("/")
async def root():
    """
    テストAPI

    Returns:
        dict[str, str]: メッセージ
    """
    return {'message": "Hello World'}
