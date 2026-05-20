from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.expense_splits import ExpenseSplit
from models.group_expenses import GroupExpense


class ExpenseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_expense(
        self, expense: GroupExpense, splits: list[ExpenseSplit]
    ) -> GroupExpense:
        self.session.add(expense)

        for split in splits:
            self.session.add(split)

        await self.session.flush()
        await self.session.refresh(expense)

        return expense

    async def get_by_id(self, expense_id: UUID) -> GroupExpense | None:
        result = await self.session.execute(
            select(GroupExpense).where(GroupExpense.id == expense_id)
        )

        return result.scalar_one_or_none()

    async def list_by_group(self, group_id: UUID) -> list[GroupExpense]:
        groups = await self.session.execute(
            select(GroupExpense).where(GroupExpense.group_id == group_id)
        )

        return list(groups.scalars().all())

    async def update_expense(self, expense: GroupExpense, data: dict) -> GroupExpense:
        for key, val in data.items():
            setattr(expense, key, val)

        await self.session.flush()
        await self.session.refresh(expense)

        return expense

    async def delete_expense(self, expense: GroupExpense) -> None:
        await self.session.delete(expense)

    async def get_splits(self, expense_id: UUID) -> list[ExpenseSplit]:
        result = await self.session.execute(
            select(ExpenseSplit).where(ExpenseSplit.expense_id == expense_id)
        )

        return list(result.scalars().all())

    async def has_pending_balance(self, group_id: UUID, user_id: UUID) -> bool:

        result = await self.session.execute(
            select(ExpenseSplit)
            .join(GroupExpense, ExpenseSplit.expense_id == GroupExpense.id)
            .where(
                GroupExpense.group_id == group_id,
                ExpenseSplit.user_id == user_id,
                ExpenseSplit.amount != 0,
            )
        )

        return result.scalar_one_or_none() is not None

    async def get_group_expense_with_splits(self, group_id: UUID) -> list[GroupExpense]:

        exp = (
            select(GroupExpense)
            .where(GroupExpense.group_id == group_id)
            .options(selectinload(GroupExpense.splits))
        )

        result = await self.session.execute(exp)
        return result.scalars().unique().all()
