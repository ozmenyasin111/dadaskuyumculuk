"""daily_baselines table

Revision ID: 0002_daily_baselines
Revises: 0001_initial
Create Date: 2026-05-14 02:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_daily_baselines"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "daily_baselines",
        sa.Column("symbol_key", sa.String(length=64), nullable=False),
        sa.Column("baseline_date", sa.Date(), nullable=False),
        sa.Column("baseline_alis", sa.Numeric(12, 4), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("symbol_key"),
    )


def downgrade() -> None:
    op.drop_table("daily_baselines")
