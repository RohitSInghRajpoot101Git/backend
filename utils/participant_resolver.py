from __future__ import (
    annotations,  # because we typing method before class created which will cause error ParticipantRef
)

from dataclasses import dataclass
from uuid import UUID

"""
Helpers for working with a participant, which may be either
a registered user or a friend.
"""


def participant_id(row) -> UUID:
    participant = row.user_id or row.friend_id
    if participant is None:
        raise ValueError("Participant has neither user_id nor friend_id.")
    return participant


def participant_name(row) -> str:
    if row.user is not None:
        return row.user.name
    if row.friend is not None:
        return row.friend.name
    raise ValueError("Participant has neither user nor friend.")


def is_friend(row) -> bool:
    return row.friend_id is not None


@dataclass(frozen=True)
class ParticipantRef:
    user_id: UUID | None = None
    friend_id: UUID | None = None

    @classmethod
    def from_user(cls, user_id: UUID) -> ParticipantRef:
        return cls(user_id=user_id)

    @classmethod
    def from_friend(cls, friend_id: UUID) -> ParticipantRef:
        return cls(friend_id=friend_id)

    def as_kwargs(self) -> dict[str, UUID | None]:
        return {
            "user_id": self.user_id,
            "friend_id": self.friend_id,
        }

    def __post_init__(self) -> None:
        if (self.user_id is None) == (self.friend_id is None):
            raise ValueError("Exactly one of user_id or friend_id must be provided.")
