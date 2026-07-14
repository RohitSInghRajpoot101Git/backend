import uuid

from sqlalchemy import TIMESTAMP, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base

"""
Foreignkey naming convention = fk_sourceTable_columnName_targetTable
index naming covention = idx_sourceTable_columnName
"""


class Friend(Base):
    __tablename__ = "friends"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )

    name = Column(String, nullable=False)

    profile_picture = Column(String, nullable=True)

    shadow_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("groups.id"),
        unique=True,
        nullable=True,
    )

    # timestamps

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # relationShips

    owner = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="friends",
    )

    shadow_group = relationship(
        "Group",
        foreign_keys=[shadow_group_id],
        back_populates="friend",
    )
