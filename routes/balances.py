from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_current_user, get_db
from models.user import User
from schemas.common import SuccessResponse
from services.balance_service import BalanceService

router = APIRouter(prefix="/groups", tags=["Balances"])


@router.get("/{group_id}/balances", response_model=SuccessResponse[dict])
async def get_group_balances(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = BalanceService(db)
    balances = await service.get_group_balances(group_id)
    return SuccessResponse(
        message="Balances fetched successfully",
        data={str(k): str(v) for k, v in balances.items()},
    )


@router.get("/{group_id}/balances/{user_id}", response_model=SuccessResponse[dict])
async def get_user_balance_in_group(
    group_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Driver code
    service = BalanceService(db)
    balances = await service.get_user_balance_in_group(user_id, group_id)
    return SuccessResponse(
        message="User balance fetched successfully",
        data={str(k): str(v) for k, v in balances.items()},
    )
