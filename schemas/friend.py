from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FriendCreate(BaseModel):
    name: str


class FriendResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    profile_picture: str | None = None
    shadow_group_id: UUID | None = None
    claimed_by_user_id: UUID | None = None
    claimed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FriendClaimRequest(BaseModel):
    token: str
