from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app import crud
from app.core.database import get_session
from app.enums import HelthCheckStatus
from app.schemas.helth_check import ResposeHelthCheck

router = APIRouter(tags=["helth_check"])


@router.get("/health-check")
async def health_check(db: AsyncSession = Depends(get_session)):
    """
    ヘルスチェックAPI
    """

    res = ResposeHelthCheck()

    # DBのヘルスチェック
    try:
        await crud.check_connection(db)
    except Exception:
        res.status = HelthCheckStatus.UNHEALTHY
        res.message = "Faild to get connection database."
        return JSONResponse(
            content=jsonable_encoder(res),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return JSONResponse(content=jsonable_encoder(res), status_code=status.HTTP_200_OK)
