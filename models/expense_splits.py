import uuid

from sqlalchemy import CheckConstraint, Column, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expense_id = Column(
        UUID(as_uuid=True), ForeignKey("group_expenses.id"), nullable=False
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    # friend
    friend_id = Column(
        UUID(as_uuid=True),
        ForeignKey("friends.id"),
        nullable=True,
    )

    # table_args
    __table_args__ = (
        CheckConstraint(
            "(user_id IS NOT NULL) <> (friend_id IS NOT NULL)",
            name="ck_expense_splits_user_xor_friend",
        ),
    )

    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String, nullable=True)

    # relationships
    expense = relationship("GroupExpense", back_populates="splits")

    user = relationship("User", back_populates="expense_splits")

    friend = relationship(
        "Friend",
        back_populates="expense_splits",
    )
