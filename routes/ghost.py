from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query, status

from schemas.ghost import (
    GhostBalanceResponse,
    GhostCreate,
    GhostDetailResponse,
    GhostResponse,
)

router = APIRouter(
    prefix="/ghosts",
    tags=["Ghosts"],
)

# TEMPORARY DUMMY DATA

dummy_ghosts = [
    {
        "id": UUID("11111111-1111-1111-1111-111111111111"),
        "name": "Rahul",
        "user_code": "GHOST-RAHUL01",
        "shadow_group_id": UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        "net_balance": Decimal("500.00"),
        "status": "owes_you",
        "expenses": [],
    },
    {
        "id": UUID("22222222-2222-2222-2222-222222222222"),
        "name": "Aman",
        "user_code": "GHOST-AMAN001",
        "shadow_group_id": UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        "net_balance": Decimal("-200.00"),
        "status": "you_owe",
        "expenses": [],
    },
    {
        "id": UUID("33333333-3333-3333-3333-333333333333"),
        "name": "Rohit",
        "user_code": "GHOST-ROHIT01",
        "shadow_group_id": UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        "net_balance": Decimal("0.00"),
        "status": "settled",
        "expenses": [],
    },
]


# HELPER FUNCTION
def find_ghost(ghost_id: UUID):
    for ghost in dummy_ghosts:
        if ghost["id"] == ghost_id:
            return ghost

    return None


# routes

#  CREATE GHOST


@router.post(
    "/",
    response_model=GhostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ghost(payload: GhostCreate):

    name = payload.name.strip()

    # Empty-name validation
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ghost name cannot be empty",
        )

    # Duplicate-name validation
    for ghost in dummy_ghosts:
        if ghost["name"].lower() == name.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already have a ghost named '{name}'",
            )
        ghost_id = uuid4()
    shadow_group_id = uuid4()

    new_ghost = {
        "id": ghost_id,
        "name": name,
        "user_code": f"GHOST-{str(ghost_id)[:8].upper()}",
        "shadow_group_id": shadow_group_id,
        # Additional internal dummy fields
        "net_balance": Decimal("0.00"),
        "status": "settled",
        "expenses": [],
    }

    dummy_ghosts.append(new_ghost)

    return new_ghost


# LIST ALL GHOSTS / SEARCH GHOSTS


@router.get(
    "/",
    response_model=list[GhostBalanceResponse],
)
async def list_ghosts(
    search: str | None = Query(default=None),
):

    ghosts = dummy_ghosts

    # Apply search filter if search query is provided
    if search:
        search_text = search.strip().lower()

        ghosts = [
            ghost for ghost in dummy_ghosts if search_text in ghost["name"].lower()
        ]

    # Sort alphabetically
    ghosts = sorted(
        ghosts,
        key=lambda ghost: ghost["name"].lower(),
    )

    # Convert internal dummy structure
    # into GhostBalanceResponse structure
    return [
        {
            "ghost_id": ghost["id"],
            "name": ghost["name"],
            "group_id": ghost["shadow_group_id"],
            "net_balance": ghost["net_balance"],
            "status": ghost["status"],
        }
        for ghost in ghosts
    ]


#  GET GHOST BALANCE


@router.get(
    "/{ghost_id}/balance",
    response_model=GhostBalanceResponse,
)
async def get_ghost_balance(ghost_id: UUID):

    ghost = find_ghost(ghost_id)

    if ghost is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ghost not found",
        )

    return {
        "ghost_id": ghost["id"],
        "name": ghost["name"],
        "group_id": ghost["shadow_group_id"],
        "net_balance": ghost["net_balance"],
        "status": ghost["status"],
    }


# 4. GET COMPLETE GHOST DETAILS


@router.get(
    "/{ghost_id}",
    response_model=GhostDetailResponse,
)
async def get_ghost_detail(ghost_id: UUID):

    ghost = find_ghost(ghost_id)

    if ghost is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ghost not found",
        )

    return {
        "ghost_id": ghost["id"],
        "name": ghost["name"],
        "group_id": ghost["shadow_group_id"],
        "net_balance": ghost["net_balance"],
        "status": ghost["status"],
        # Empty for now because PersonalExpense repository/service
        # is not being used in this temporary route.
        "expenses": ghost["expenses"],
    }


#  DELETE GHOST


@router.delete(
    "/{ghost_id}",
)
async def delete_ghost(ghost_id: UUID):

    ghost = find_ghost(ghost_id)

    if ghost is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ghost not found",
        )

    # Don't allow deletion if balance is pending
    if ghost["net_balance"] != Decimal("0.00"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("Ghost has a pending balance and cannot be deleted"),
        )

    dummy_ghosts.remove(ghost)

    return {
        "message": "Ghost deleted successfully",
        "data": None,
    }
