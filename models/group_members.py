import uuid
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, CheckConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class Role(Enum):
    ADMIN = "admin"
    MEMBER = "member"


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # made nullable for friend
    # friend
    friend_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("friends.id"), 
        nullable=True
    )
    
    role = Column(
        SQLEnum(Role), nullable=False, default=Role.MEMBER
    )  # "admin" or "member"
    joined_at = Column(DateTime, server_default=func.now())

    # table_args
    __table_args__ = (
        CheckConstraint(
            "(user_id IS NOT NULL) <> (friend_id IS NOT NULL)",
            name="ck_group_members_user_xor_friend",
        ),
    )
    
    # relationships
    group = relationship("Group", back_populates="members")
    # user = relationship("User", back_populates="group_memberships")

    user = relationship(
        "User",
        back_populates="group_memberships",
    )

    friend = relationship(
        "Friend",
        back_populates="group_memberships",
    )


    @property
    def name(self) -> str:
        if self.user:
            return self.user.name
        if self.friend:
            return self.friend.name
        return ""
