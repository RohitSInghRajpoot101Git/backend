from decimal import Decimal
from uuid import uuid4

from engines.sync_engine import (
    compute_personal_records_for_expense,
    diff_personal_records,
)

# ── compute_personal_records_for_expense ─────────────────────────────────────


def test_creates_one_record_per_split_participant():
    expense_id = uuid4()
    group_id = uuid4()
    paid_by = uuid4()
    user_a = uuid4()
    user_b = uuid4()

    splits = [
        {"user_id": paid_by, "amount": Decimal("100.00")},
        {"user_id": user_a, "amount": Decimal("100.00")},
        {"user_id": user_b, "amount": Decimal("100.00")},
    ]

    records = compute_personal_records_for_expense(
        expense_id=expense_id,
        group_id=group_id,
        title="Dinner",
        paid_by=paid_by,
        splits=splits,
    )

    assert len(records) == 3
    user_ids = {r["user_id"] for r in records}
    assert user_ids == {paid_by, user_a, user_b}


def test_each_record_carries_correct_amount():
    expense_id = uuid4()
    group_id = uuid4()
    paid_by = uuid4()
    user_a = uuid4()

    splits = [
        {"user_id": paid_by, "amount": Decimal("60.00")},
        {"user_id": user_a, "amount": Decimal("40.00")},
    ]

    records = compute_personal_records_for_expense(
        expense_id=expense_id,
        group_id=group_id,
        title="Taxi",
        paid_by=paid_by,
        splits=splits,
    )

    by_user = {r["user_id"]: r for r in records}
    assert by_user[paid_by]["amount"] == Decimal("60.00")
    assert by_user[user_a]["amount"] == Decimal("40.00")


def test_records_carry_correct_foreign_keys():
    expense_id = uuid4()
    group_id = uuid4()
    paid_by = uuid4()

    splits = [{"user_id": paid_by, "amount": Decimal("50.00")}]

    records = compute_personal_records_for_expense(
        expense_id=expense_id,
        group_id=group_id,
        title="Coffee",
        paid_by=paid_by,
        splits=splits,
    )

    assert records[0]["group_id"] == group_id
    assert records[0]["group_expense_id"] == expense_id


def test_category_is_none_so_user_can_set_it_later():
    paid_by = uuid4()
    splits = [{"user_id": paid_by, "amount": Decimal("25.00")}]

    records = compute_personal_records_for_expense(
        expense_id=uuid4(),
        group_id=uuid4(),
        title="Snacks",
        paid_by=paid_by,
        splits=splits,
    )

    assert records[0]["category"] is None


def test_title_is_propagated_to_all_records():
    paid_by = uuid4()
    user_a = uuid4()
    splits = [
        {"user_id": paid_by, "amount": Decimal("50.00")},
        {"user_id": user_a, "amount": Decimal("50.00")},
    ]

    records = compute_personal_records_for_expense(
        expense_id=uuid4(),
        group_id=uuid4(),
        title="Hotel Stay",
        paid_by=paid_by,
        splits=splits,
    )

    assert all(r["title"] == "Hotel Stay" for r in records)


def test_empty_splits_returns_empty_list():
    records = compute_personal_records_for_expense(
        expense_id=uuid4(),
        group_id=uuid4(),
        title="Ghost Expense",
        paid_by=uuid4(),
        splits=[],
    )

    assert records == []


def test_string_amounts_are_coerced_to_decimal():
    paid_by = uuid4()
    splits = [{"user_id": paid_by, "amount": "33.33"}]

    records = compute_personal_records_for_expense(
        expense_id=uuid4(),
        group_id=uuid4(),
        title="Lunch",
        paid_by=paid_by,
        splits=splits,
    )

    assert isinstance(records[0]["amount"], Decimal)
    assert records[0]["amount"] == Decimal("33.33")


# ── diff_personal_records ─────────────────────────────────────────────────────


def test_all_new_users_go_into_to_create():
    user_a = uuid4()
    user_b = uuid4()
    group_id = uuid4()
    expense_id = uuid4()

    desired = [
        {
            "user_id": user_a,
            "group_id": group_id,
            "group_expense_id": expense_id,
            "title": "Dinner",
            "amount": Decimal("100.00"),
        },
        {
            "user_id": user_b,
            "group_id": group_id,
            "group_expense_id": expense_id,
            "title": "Dinner",
            "amount": Decimal("100.00"),
        },
    ]

    to_create, to_update, to_delete = diff_personal_records(
        existing=[], desired=desired
    )

    assert len(to_create) == 2
    assert to_update == []
    assert to_delete == []


def test_unchanged_record_produces_no_diff():
    user_a = uuid4()
    record_id = uuid4()

    existing = [
        {
            "id": record_id,
            "user_id": user_a,
            "title": "Dinner",
            "amount": Decimal("100.00"),
        }
    ]
    desired = [
        {
            "user_id": user_a,
            "group_id": uuid4(),
            "group_expense_id": uuid4(),
            "title": "Dinner",
            "amount": Decimal("100.00"),
        }
    ]

    to_create, to_update, to_delete = diff_personal_records(existing, desired)

    assert to_create == []
    assert to_update == []
    assert to_delete == []


def test_amount_change_triggers_update():
    user_a = uuid4()
    record_id = uuid4()

    existing = [
        {
            "id": record_id,
            "user_id": user_a,
            "title": "Dinner",
            "amount": Decimal("100.00"),
        }
    ]
    desired = [
        {
            "user_id": user_a,
            "group_id": uuid4(),
            "group_expense_id": uuid4(),
            "title": "Dinner",
            "amount": Decimal("120.00"),
        }
    ]

    to_create, to_update, to_delete = diff_personal_records(existing, desired)

    assert to_create == []
    assert len(to_update) == 1
    assert to_update[0]["id"] == record_id
    assert to_update[0]["amount"] == Decimal("120.00")
    assert to_delete == []


def test_title_change_triggers_update():
    user_a = uuid4()
    record_id = uuid4()

    existing = [
        {
            "id": record_id,
            "user_id": user_a,
            "title": "Old Title",
            "amount": Decimal("50.00"),
        }
    ]
    desired = [
        {
            "user_id": user_a,
            "group_id": uuid4(),
            "group_expense_id": uuid4(),
            "title": "New Title",
            "amount": Decimal("50.00"),
        }
    ]

    to_create, to_update, to_delete = diff_personal_records(existing, desired)

    assert len(to_update) == 1
    assert to_update[0]["title"] == "New Title"
    assert to_create == []
    assert to_delete == []


def test_user_removed_from_split_goes_into_to_delete():
    user_a = uuid4()
    user_b = uuid4()
    record_a_id = uuid4()
    record_b_id = uuid4()

    existing = [
        {
            "id": record_a_id,
            "user_id": user_a,
            "title": "Trip",
            "amount": Decimal("100.00"),
        },
        {
            "id": record_b_id,
            "user_id": user_b,
            "title": "Trip",
            "amount": Decimal("100.00"),
        },
    ]
    # user_b removed from split
    desired = [
        {
            "user_id": user_a,
            "group_id": uuid4(),
            "group_expense_id": uuid4(),
            "title": "Trip",
            "amount": Decimal("100.00"),
        }
    ]

    to_create, to_update, to_delete = diff_personal_records(existing, desired)

    assert to_create == []
    assert to_update == []
    assert len(to_delete) == 1
    assert to_delete[0]["id"] == record_b_id


def test_new_user_added_to_split_goes_into_to_create():
    user_a = uuid4()
    user_b = uuid4()
    record_a_id = uuid4()
    group_id = uuid4()
    expense_id = uuid4()

    existing = [
        {
            "id": record_a_id,
            "user_id": user_a,
            "title": "Trip",
            "amount": Decimal("100.00"),
        }
    ]
    desired = [
        {
            "user_id": user_a,
            "group_id": group_id,
            "group_expense_id": expense_id,
            "title": "Trip",
            "amount": Decimal("100.00"),
        },
        {
            "user_id": user_b,
            "group_id": group_id,
            "group_expense_id": expense_id,
            "title": "Trip",
            "amount": Decimal("100.00"),
        },
    ]

    to_create, to_update, to_delete = diff_personal_records(existing, desired)

    assert len(to_create) == 1
    assert to_create[0]["user_id"] == user_b
    assert to_update == []
    assert to_delete == []


def test_full_replacement_all_three_buckets_populated():
    user_a = uuid4()
    user_b = uuid4()
    user_c = uuid4()
    record_a_id = uuid4()
    record_b_id = uuid4()
    group_id = uuid4()
    expense_id = uuid4()

    existing = [
        # user_a: amount will change → to_update
        {
            "id": record_a_id,
            "user_id": user_a,
            "title": "Goa Trip",
            "amount": Decimal("200.00"),
        },
        # user_b: no longer in split → to_delete
        {
            "id": record_b_id,
            "user_id": user_b,
            "title": "Goa Trip",
            "amount": Decimal("200.00"),
        },
    ]
    desired = [
        # user_a: updated amount
        {
            "user_id": user_a,
            "group_id": group_id,
            "group_expense_id": expense_id,
            "title": "Goa Trip",
            "amount": Decimal("300.00"),
        },
        # user_c: brand new → to_create
        {
            "user_id": user_c,
            "group_id": group_id,
            "group_expense_id": expense_id,
            "title": "Goa Trip",
            "amount": Decimal("100.00"),
        },
    ]

    to_create, to_update, to_delete = diff_personal_records(existing, desired)

    assert len(to_create) == 1
    assert to_create[0]["user_id"] == user_c

    assert len(to_update) == 1
    assert to_update[0]["id"] == record_a_id
    assert to_update[0]["amount"] == Decimal("300.00")

    assert len(to_delete) == 1
    assert to_delete[0]["id"] == record_b_id


def test_diff_with_empty_existing_and_empty_desired_returns_all_empty():
    to_create, to_update, to_delete = diff_personal_records(existing=[], desired=[])
    assert to_create == []
    assert to_update == []
    assert to_delete == []


def test_diff_update_carries_both_id_title_and_amount():
    user_a = uuid4()
    record_id = uuid4()

    existing = [
        {"id": record_id, "user_id": user_a, "title": "Old", "amount": Decimal("10.00")}
    ]
    desired = [
        {
            "user_id": user_a,
            "group_id": uuid4(),
            "group_expense_id": uuid4(),
            "title": "New",
            "amount": Decimal("20.00"),
        }
    ]

    _, to_update, _ = diff_personal_records(existing, desired)

    assert to_update[0].keys() >= {"id", "title", "amount"}
