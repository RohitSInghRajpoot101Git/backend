from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.personal_expenses import PersonalExpense


class SyncRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_create_expense(
        self, expenses: list[PersonalExpense]
    ) -> list[PersonalExpense]:
        for expense in expenses:
            self.session.add(expense)
        await self.session.commit()
        for expense in expenses:
            await self.session.refresh(expense)
        return expenses

    async def get_sync_group_expenses(
        self, group_expense_id: UUID
    ) -> list[PersonalExpense]:
        result = await self.session.execute(
            select(PersonalExpense).where(
                PersonalExpense.group_expense_id == group_expense_id
            )
        )
        return list(result.scalars().all())

    async def get_by_ids(self, ids: list[UUID]) -> list[PersonalExpense]:
        if not ids:
            return []
        result = await self.session.execute(
            select(PersonalExpense).where(PersonalExpense.id.in_(ids))
        )

        return list(result.scalars().all())

    async def bulk_delete_expense(self, expenses: list[PersonalExpense]) -> int:
        for expense in expenses:
            await self.session.delete(expense)
        await self.session.commit()
        return len(expenses)
