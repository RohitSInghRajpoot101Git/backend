from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi import HTTPException

from engines.split_engine import calculate_splits


def test_equal_split_defaults_to_all_group_members():
    members = [uuid4(), uuid4(), uuid4(), uuid4()]

    result = calculate_splits(
        total_amount=Decimal("100.00"),
        all_members_id=members,
        split_type="equal",
    )

    assert result == {member: Decimal("25.00") for member in members}


def test_equal_split_can_target_member_subset():
    members = [uuid4(), uuid4(), uuid4(), uuid4(), uuid4()]
    selected_members = members[:3]

    result = calculate_splits(
        total_amount=Decimal("99.99"),
        all_members_id=members,
        split_type="equal",
        equal_member_ids=selected_members,
    )

    assert result == {member: Decimal("33.33") for member in selected_members}
    assert members[3] not in result
    assert members[4] not in result


def test_equal_split_rejects_non_group_member():
    members = [uuid4(), uuid4()]
    outsider = uuid4()

    with pytest.raises(HTTPException) as exc_info:
        calculate_splits(
            total_amount=Decimal("100.00"),
            all_members_id=members,
            split_type="equal",
            equal_member_ids=[members[0], outsider],
        )

    assert exc_info.value.status_code == 400
    assert "not group members" in exc_info.value.detail


def test_exact_split_accepts_decimal_values_that_match_total():
    members = [uuid4(), uuid4(), uuid4(), uuid4()]
    splits_input = {
        members[0]: Decimal("10.10"),
        members[1]: Decimal("20.20"),
        members[2]: Decimal("30.30"),
        members[3]: Decimal("40.40"),
    }

    result = calculate_splits(
        total_amount=Decimal("101.00"),
        all_members_id=members,
        split_type="exact",
        splits_input=splits_input,
    )

    assert result == splits_input


def test_exact_split_rejects_missing_input():
    with pytest.raises(HTTPException) as exc_info:
        calculate_splits(
            total_amount=Decimal("100.00"),
            all_members_id=[uuid4()],
            split_type="exact",
        )

    assert exc_info.value.status_code == 400
    assert "required for exact split" in exc_info.value.detail


def test_exact_split_rejects_total_mismatch():
    members = [uuid4(), uuid4()]

    with pytest.raises(HTTPException) as exc_info:
        calculate_splits(
            total_amount=Decimal("100.00"),
            all_members_id=members,
            split_type="exact",
            splits_input={
                members[0]: Decimal("40.00"),
                members[1]: Decimal("59.99"),
            },
        )

    assert exc_info.value.status_code == 400
    assert "must sum to 100.00" in exc_info.value.detail


def test_exact_split_rejects_non_group_member():
    members = [uuid4(), uuid4()]
    outsider = uuid4()

    with pytest.raises(HTTPException) as exc_info:
        calculate_splits(
            total_amount=Decimal("100.00"),
            all_members_id=members,
            split_type="exact",
            splits_input={
                members[0]: Decimal("50.00"),
                outsider: Decimal("50.00"),
            },
        )

    assert exc_info.value.status_code == 400
    assert "not group members" in exc_info.value.detail


def test_percentage_split_converts_percentages_to_amounts():
    members = [uuid4(), uuid4(), uuid4(), uuid4(), uuid4()]

    result = calculate_splits(
        total_amount=Decimal("8888.80"),
        all_members_id=members,
        split_type="percentage",
        splits_input={
            members[0]: Decimal("30"),
            members[1]: Decimal("25"),
            members[2]: Decimal("20"),
            members[3]: Decimal("15"),
            members[4]: Decimal("10"),
        },
    )

    assert result == {
        members[0]: Decimal("2666.64"),
        members[1]: Decimal("2222.20"),
        members[2]: Decimal("1777.76"),
        members[3]: Decimal("1333.32"),
        members[4]: Decimal("888.88"),
    }


def test_percentage_split_rejects_missing_input():
    with pytest.raises(HTTPException) as exc_info:
        calculate_splits(
            total_amount=Decimal("100.00"),
            all_members_id=[uuid4()],
            split_type="percentage",
        )

    assert exc_info.value.status_code == 400
    assert "required for percentage" in exc_info.value.detail


def test_percentage_split_rejects_percentage_total_mismatch():
    members = [uuid4(), uuid4()]

    with pytest.raises(HTTPException) as exc_info:
        calculate_splits(
            total_amount=Decimal("100.00"),
            all_members_id=members,
            split_type="percentage",
            splits_input={
                members[0]: Decimal("75"),
                members[1]: Decimal("20"),
            },
        )

    assert exc_info.value.status_code == 400
    assert "must sum to 100" in exc_info.value.detail


def test_percentage_split_rejects_non_group_member():
    members = [uuid4(), uuid4()]
    outsider = uuid4()

    with pytest.raises(HTTPException) as exc_info:
        calculate_splits(
            total_amount=Decimal("100.00"),
            all_members_id=members,
            split_type="percentage",
            splits_input={
                members[0]: Decimal("50"),
                outsider: Decimal("50"),
            },
        )

    assert exc_info.value.status_code == 400
    assert "not group members" in exc_info.value.detail


def test_invalid_split_type_is_rejected():
    with pytest.raises(HTTPException) as exc_info:
        calculate_splits(
            total_amount=Decimal("100.00"),
            all_members_id=[uuid4()],
            split_type="shares",
        )

    assert exc_info.value.status_code == 400
    assert "Invalid split type" in exc_info.value.detail
