import uuid
from sqlalchemy import Column, String, TIMESTAMP , Boolean , Enum as SQLEnum #type: ignore
from sqlalchemy.dialects.postgresql import UUID#type: ignore
from sqlalchemy.sql import func #type: ignore

from sqlalchemy.orm import relationship
from database import Base
from enum import Enum

class AuthProvider(Enum):
    LOCAL = 'local'
    GOOGLE = 'google'
    
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=True)
    google_id = Column(String, unique=True, nullable=True)
    auth_provider = Column(SQLEnum(AuthProvider), nullable=False, default=AuthProvider.LOCAL) 
    profile_picture = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # relationships
    groups = relationship("Group", back_populates="creator")
    group_memberships = relationship("GroupMember", back_populates="user")
    expenses_paid = relationship("GroupExpense", foreign_keys="GroupExpense.paid_by", back_populates="payer")
    expense_splits = relationship("ExpenseSplit", back_populates="user")
    payments_made = relationship("Settlement", foreign_keys="Settlement.payer_id", back_populates="payer")
    payments_received = relationship("Settlement", foreign_keys="Settlement.receiver_id", back_populates="receiver")