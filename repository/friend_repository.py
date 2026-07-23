from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.friend import Friend
from models.groups import Group
from models.group_members import GroupMember
from models.expense_splits import ExpenseSplit
from models.settlements import Settlement

class FriendRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_friend(self, friend: Friend) -> Friend:
        """
        Persist a new Friend
        FIXME:
        friend_service.create_friend needs Friend → Group → two GroupMember rows in one transaction. If this method commits after inserting just the owner's GroupMember, and the second insert (the friend's GroupMember) then fails, you're left with a group that has an owner but no friend slot — a broken half-created shadow group, silently committed, un-rollback-able.
        """
        self.session.add(friend)
        await self.session.commit()
        await self.session.refresh(friend)
        return friend
    
    async def get_by_id(self, friend_id: UUID) -> Friend | None:
        """
        Fetch a friend by its ID.
        """
        result = await self.session.execute(
            select(Friend).where(Friend.id == friend_id)
        )
        return result.scalar_one_or_none()
    
    async def get_shadow_group(self, friend_id: UUID) -> Group | None:
        """
        Return the friend's shadow group.
        """
        result = await self.session.execute(
            select(Group)
            .join(Friend, Friend.shadow_group_id == Group.id)
            .where(Friend.id == friend_id)
        )
        return result.scalar_one_or_none()
    
    async def mark_claimed(
        self,
        friend: Friend,
        claimed_by_user_id: UUID,
    ) -> Friend:
        """
         Mark a friend as claimed by a real user.
        """
        friend.claimed_by_user_id = claimed_by_user_id

        await self.session.flush()
        await self.session.refresh(friend)

        return friend
    
    async def delete_friend(self, friend: Friend) -> None:
        """
        Delete a friend.
        """
        await self.session.delete(friend)
        await self.session.commit()
        
    # Claiming  Process
    async def rewrite_group_members(
        self,
        friend_id: UUID,
        user_id: UUID,
    ) -> None:
        """
        Replace friend participants with a real user in group members.
        """
        await self.session.execute(
            update(GroupMember)
            .where(GroupMember.friend_id == friend_id)
            .values(
                user_id=user_id,
                friend_id=None,
            )
        )
        
        
    async def rewrite_expense_splits(
        self,
        friend_id: UUID,
        user_id: UUID,
    ) -> None:
        """
        Replace friend participants with a real user in expense splits.
        """
        await self.session.execute(
            update(ExpenseSplit)
            .where(ExpenseSplit.friend_id == friend_id)
            .values(
                user_id=user_id,
                friend_id=None,
            )
        )
        
        
    async def rewrite_settlements(
        self,
        friend_id: UUID,
        user_id: UUID,
    ) -> None:
        """
        Replace friend participants with a real user in settlements.
        """
        # Friend was payer
        await self.session.execute(
            update(Settlement)
            .where(Settlement.payer_friend_id == friend_id)
            .values(
                payer_id=user_id,
                payer_friend_id=None,
            )
        )

        # Friend was receiver
        await self.session.execute(
            update(Settlement)
            .where(Settlement.receiver_friend_id == friend_id)
            .values(
                receiver_id=user_id,
                receiver_friend_id=None,
            )
        )
        
    async def has_nonzero_splits(self, friend_id: UUID) -> bool:
        result = await self.session.execute(
            select(ExpenseSplit).where(
                ExpenseSplit.friend_id == friend_id, ExpenseSplit.amount != 0
            )
        )
        return result.scalar_one_or_none() is not None
    
    # async def is_claimed(self, friend_id: UUID) -> bool:
    #     """
    #     Return True if the friend has already been claimed.
    #     """
    #     result = await self.session.execute(
    #         select(Friend.claimed_by_user_id).where(Friend.id == friend_id)
    #     )

    #     claimed_by = result.scalar_one_or_none()
    #     return claimed_by is not None