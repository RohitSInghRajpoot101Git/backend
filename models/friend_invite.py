import uuid

from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class FriendInvite(Base):
    __tablename__ = "friend_invites"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    friend_id = Column(
        UUID(as_uuid=True),
        ForeignKey("friends.id"),
        nullable=False,
    )

    token_hash = Column(
        String,
        nullable=False,
        unique=True,
    )

    expires_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )

    used = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    friend = relationship(
        "Friend",
        back_populates="invites",
    )