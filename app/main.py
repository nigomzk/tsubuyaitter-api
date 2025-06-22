from fastapi import FastAPI, APIRouter
from app.routes import auth

app = FastAPI()
app.include_router(auth.router)

@app.get('/')
async def root():
    return {'message": "Hello World'}