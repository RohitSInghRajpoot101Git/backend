from decimal import Decimal
from uuid import uuid4

from engines.debt_breakdown_engine import (
    aggregate_debt,
    build_debt_breakdown,
    calculate_net_balance,
    settle_debts,
    simplify_debt,
)


def test_build_debt_breakdown():
    payer = uuid4()
    user1 = uuid4()
    user2 = uuid4()

    expenses = [
        {
            "expense_id": uuid4(),
            "title": "Dinner",
            "paid_by": payer,
            "splits": [
                {
                    "user_id": payer,
                    "amount": Decimal("100"),
                },
                {
                    "user_id": user1,
                    "amount": Decimal("100"),
                },
                {
                    "user_id": user2,
                    "amount": Decimal("100"),
                },
            ],
        }
    ]

    result = build_debt_breakdown(expenses)

    assert result == {
        user1: {
            payer: [
                {
                    "expense_id": expenses[0]["expense_id"],
                    "title": "Dinner",
                    "amount": Decimal("100"),
                }
            ]
        },
        user2: {
            payer: [
                {
                    "expense_id": expenses[0]["expense_id"],
                    "title": "Dinner",
                    "amount": Decimal("100"),
                }
            ]
        },
    }


def test_aggregate_debt():
    debtor = uuid4()
    creditor = uuid4()

    breakdown = {
        debtor: {
            creditor: [
                {"amount": Decimal("100")},
                {"amount": Decimal("50")},
            ]
        }
    }

    result = aggregate_debt(breakdown)

    assert result == {
        debtor: {
            creditor: Decimal("150"),
        }
    }


def test_simplify_debt():
    user_a = uuid4()
    user_b = uuid4()

    aggregated = {
        user_a: {
            user_b: Decimal("500"),
        },
        user_b: {
            user_a: Decimal("200"),
        },
    }

    result = simplify_debt(aggregated)

    assert result == {
        user_a: {
            user_b: Decimal("300"),
        }
    }


def test_settle_debts_chain_simplification():
    user_a = uuid4()
    user_b = uuid4()
    user_c = uuid4()

    aggregated = {
        user_a: {
            user_b: Decimal("100"),
        },
        user_b: {
            user_c: Decimal("100"),
        },
    }

    result = settle_debts(aggregated)

    assert result == {
        user_a: {
            user_c: Decimal("100"),
        }
    }


def test_settle_debts_multiple_debtors():
    creditor = uuid4()
    debtor1 = uuid4()
    debtor2 = uuid4()

    aggregated = {
        debtor1: {
            creditor: Decimal("200"),
        },
        debtor2: {
            creditor: Decimal("300"),
        },
    }

    result = settle_debts(aggregated)

    assert result == {
        debtor1: {
            creditor: Decimal("200"),
        },
        debtor2: {
            creditor: Decimal("300"),
        },
    }


def test_settle_debts_removes_intermediate_users():
    user_a = uuid4()
    user_b = uuid4()
    user_c = uuid4()
    user_d = uuid4()

    aggregated = {
        user_a: {
            user_b: Decimal("100"),
        },
        user_b: {
            user_c: Decimal("100"),
        },
        user_c: {
            user_d: Decimal("100"),
        },
    }

    result = settle_debts(aggregated)

    assert result == {
        user_a: {
            user_d: Decimal("100"),
        }
    }


def test_build_debt_breakdown_handles_multiple_expenses_and_decimal_strings():
    payer_a = uuid4()
    payer_b = uuid4()
    debtor_c = uuid4()
    debtor_d = uuid4()
    first_expense_id = uuid4()
    second_expense_id = uuid4()

    expenses = [
        {
            "expense_id": first_expense_id,
            "title": "Groceries",
            "paid_by": payer_a,
            "splits": [
                {"user_id": payer_a, "amount": Decimal("25.00")},
                {"user_id": payer_b, "amount": "10.50"},
                {"user_id": debtor_c, "amount": Decimal("35.25")},
            ],
        },
        {
            "expense_id": second_expense_id,
            "title": "Taxi",
            "paid_by": payer_b,
            "splits": [
                {"user_id": payer_a, "amount": Decimal("12.10")},
                {"user_id": payer_b, "amount": Decimal("12.10")},
                {"user_id": debtor_d, "amount": "24.20"},
            ],
        },
    ]

    result = build_debt_breakdown(expenses)

    assert result == {
        payer_b: {
            payer_a: [
                {
                    "expense_id": first_expense_id,
                    "title": "Groceries",
                    "amount": Decimal("10.50"),
                }
            ]
        },
        debtor_c: {
            payer_a: [
                {
                    "expense_id": first_expense_id,
                    "title": "Groceries",
                    "amount": Decimal("35.25"),
                }
            ]
        },
        payer_a: {
            payer_b: [
                {
                    "expense_id": second_expense_id,
                    "title": "Taxi",
                    "amount": Decimal("12.10"),
                }
            ]
        },
        debtor_d: {
            payer_b: [
                {
                    "expense_id": second_expense_id,
                    "title": "Taxi",
                    "amount": Decimal("24.20"),
                }
            ]
        },
    }


def test_aggregate_debt_keeps_independent_creditors_separate():
    debtor = uuid4()
    creditor_a = uuid4()
    creditor_b = uuid4()

    breakdown = {
        debtor: {
            creditor_a: [
                {"amount": Decimal("100.25")},
                {"amount": Decimal("50.75")},
            ],
            creditor_b: [
                {"amount": Decimal("10.10")},
                {"amount": Decimal("20.20")},
            ],
        }
    }

    result = aggregate_debt(breakdown)

    assert result == {
        debtor: {
            creditor_a: Decimal("151.00"),
            creditor_b: Decimal("30.30"),
        }
    }


def test_simplify_debt_removes_equal_reverse_debts():
    user_a = uuid4()
    user_b = uuid4()

    aggregated = {
        user_a: {user_b: Decimal("75.25")},
        user_b: {user_a: Decimal("75.25")},
    }

    assert simplify_debt(aggregated) == {}


def test_simplify_debt_keeps_only_larger_reverse_direction():
    user_a = uuid4()
    user_b = uuid4()
    user_c = uuid4()

    aggregated = {
        user_a: {
            user_b: Decimal("40.00"),
            user_c: Decimal("12.00"),
        },
        user_b: {
            user_a: Decimal("95.50"),
        },
    }

    result = simplify_debt(aggregated)

    assert result == {
        user_a: {
            user_c: Decimal("12.00"),
        },
        user_b: {
            user_a: Decimal("55.50"),
        },
    }


def test_settle_debts_balances_complex_multi_party_graph():
    alice = uuid4()
    bob = uuid4()
    carol = uuid4()
    drew = uuid4()
    emma = uuid4()

    aggregated = {
        alice: {
            bob: Decimal("50.00"),
            carol: Decimal("50.00"),
        },
        drew: {
            carol: Decimal("30.00"),
        },
        bob: {
            emma: Decimal("20.00"),
        },
    }

    result = settle_debts(aggregated)

    assert result == {
        alice: {
            bob: Decimal("30.00"),
            carol: Decimal("70.00"),
        },
        drew: {
            carol: Decimal("10.00"),
            emma: Decimal("20.00"),
        },
    }
    assert calculate_net_balance(result, alice) == Decimal("-100.00")
    assert calculate_net_balance(result, bob) == Decimal("30.00")
    assert calculate_net_balance(result, carol) == Decimal("80.00")
    assert calculate_net_balance(result, drew) == Decimal("-30.00")
    assert calculate_net_balance(result, emma) == Decimal("20.00")


def test_settle_debts_rounds_tiny_residuals_to_cents():
    debtor = uuid4()
    creditor = uuid4()

    aggregated = {
        debtor: {
            creditor: Decimal("10.005"),
        }
    }

    assert settle_debts(aggregated) == {
        debtor: {
            creditor: Decimal("10.00"),
        }
    }


def test_calculate_net_balance_for_debtor_creditor_and_unknown_user():
    debtor = uuid4()
    creditor = uuid4()
    third_user = uuid4()
    unknown_user = uuid4()

    aggregated = {
        debtor: {
            creditor: Decimal("90.00"),
        },
        third_user: {
            debtor: Decimal("25.50"),
        },
    }

    assert calculate_net_balance(aggregated, debtor) == Decimal("-64.50")
    assert calculate_net_balance(aggregated, creditor) == Decimal("90.00")
    assert calculate_net_balance(aggregated, third_user) == Decimal("-25.50")
    assert calculate_net_balance(aggregated, unknown_user) == Decimal("0")
