from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app import crud
from app.core import redis
from app.core.database import get_session
from app.enums import HealthCheckStatus
from app.schemas.health_check import HealthCheckItem, ResposeHealthCheck

router = APIRouter(tags=["health_check"])


@router.get("/health-check")
async def health_check(
    db: AsyncSession = Depends(get_session), redis_client: Redis = Depends(redis.get_redis_client)
):
    """
    ヘルスチェックAPI
    """

    res = ResposeHealthCheck()
    status_code = status.HTTP_200_OK

    # DBのヘルスチェック
    db_health_check = HealthCheckItem(name="database")
    try:
        await crud.check_connection(db)
    except Exception:
        res.status = HealthCheckStatus.UNHEALTHY
        res.message = "Faild to connect servers."
        db_health_check.status = HealthCheckStatus.UNHEALTHY
        db_health_check.message = "Faild to get connection database."
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    res.contents.append(db_health_check)

    # redisのヘルスチェック
    redis_health_check = HealthCheckItem(name="redis")
    try:
        await redis.check_connection(redis_client)
    except Exception as e:
        print(e)
        res.status = HealthCheckStatus.UNHEALTHY
        res.message = "Faild to connect servers."
        redis_health_check.status = HealthCheckStatus.UNHEALTHY
        redis_health_check.message = "Faild to get connection redis."
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    res.contents.append(redis_health_check)

    return JSONResponse(content=jsonable_encoder(res), status_code=status_code)
