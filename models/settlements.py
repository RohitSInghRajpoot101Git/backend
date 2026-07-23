import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, CheckConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base
from models.group_expenses import PaymentMethod


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    
    payer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # user 
    payer_friend_id = Column(UUID(as_uuid=True), ForeignKey("friends.id"), nullable=True)
    
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True) # user
    receiver_friend_id = Column(UUID(as_uuid=True), ForeignKey("friends.id"), nullable=True)
    
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # table args
    __table_args__ = (
        CheckConstraint(
            "(payer_id IS NOT NULL) <> (payer_friend_id IS NOT NULL)",
            name="ck_settlement_payer_xor",
        ),
        CheckConstraint(
            "(receiver_id IS NOT NULL) <> (receiver_friend_id IS NOT NULL)",
            name="ck_settlement_receiver_xor",
        ),   
    )

    # relationships
    group = relationship("Group", back_populates="settlements")
    
    payer = relationship(
        "User", foreign_keys=[payer_id], back_populates="payments_made"
    )
    receiver = relationship(
        "User", foreign_keys=[receiver_id], back_populates="payments_received"
    )

    payer_friend = relationship(
        "Friend",
        foreign_keys=[payer_friend_id],
        back_populates="payments_made",
    )


    receiver_friend = relationship(
        "Friend",
        foreign_keys=[receiver_friend_id],
        back_populates="payments_received",
    )
