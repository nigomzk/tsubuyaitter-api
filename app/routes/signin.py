from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.redis import get_redis_client
from app.schemas import token_schema
from app.services import token_service, user_service

router = APIRouter(tags=["signin"])


@router.post("/signin", status_code=status.HTTP_200_OK)
async def signin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_client),
) -> token_schema.Token:
    """
    サインインAPI
    """
    # 認証実施
    user = await user_service.authenticate_user(db, form_data.username, form_data.password)

    # トークン返却
    return await token_service.create_tokens(user, redis)
