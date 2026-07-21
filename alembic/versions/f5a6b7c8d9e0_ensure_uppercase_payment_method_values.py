"""ensure uppercase payment_method enum values

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-07-21 16:55:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'f5a6b7c8d9e0'
down_revision: Union[str, Sequence[str], None] = 'e4f5a6b7c8d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            ALTER TYPE paymentmethod RENAME VALUE 'upi' TO 'UPI';
        EXCEPTION
            WHEN undefined_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            ALTER TYPE paymentmethod RENAME VALUE 'cash' TO 'CASH';
        EXCEPTION
            WHEN undefined_object THEN NULL;
        END $$;
    """)


def downgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            ALTER TYPE paymentmethod RENAME VALUE 'UPI' TO 'upi';
        EXCEPTION
            WHEN undefined_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
            ALTER TYPE paymentmethod RENAME VALUE 'CASH' TO 'cash';
        EXCEPTION
            WHEN undefined_object THEN NULL;
        END $$;
    """)