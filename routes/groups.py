from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_current_user, get_db
from models.user import User
from schemas.common import SuccessResponse
from schemas.groups import GroupCreate, GroupResponse, GroupUpdate
from services.group_service import (
    create_group,
    delete_group,
    get_group,
    list_groups,
    update_group,
)

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.post(
    "/",
    response_model=SuccessResponse[GroupResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create(
    group_data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await create_group(group_data, db, user.id)


@router.get("/", response_model=SuccessResponse[list[GroupResponse]])
async def list_users(
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    return await list_groups(db, user.id)


@router.get("/{group_id}", response_model=SuccessResponse[GroupResponse])
async def get_groups_by_user(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await get_group(db, group_id, user.id)


@router.put("/{group_id}", response_model=SuccessResponse[GroupResponse])
async def update_groups_by_user(
    group_id: UUID,
    group_data: GroupUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await update_group(db, group_id, group_data, user.id)


@router.delete(
    "/{group_id}", response_model=SuccessResponse[None], status_code=status.HTTP_200_OK
)
async def delete_groups_by_user(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await delete_group(group_id, user.id, db)
