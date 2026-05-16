"""Pricing mode toggle: milyem | classic (TL ekle/çıkar)

Revision ID: 0007_pricing_mode
Revises: 0006_kulcealtin
Create Date: 2026-05-16 09:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_pricing_mode"
down_revision: Union[str, None] = "0006_kulcealtin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (symbol_key, classic_alis_offset, classic_satis_offset)
# Plan'daki orijinal "Fiyat Ekle/Çıkar" default değerleri.
CLASSIC_DEFAULTS = [
    ("SARRAFIYE.AYAR22", -15, 100),
    ("SARRAFIYE.AYAR14", 0, 700),
    ("SARRAFIYE.CEYREK_YENI", -100, 200),
    ("SARRAFIYE.CEYREK_ESKI", -100, 200),
    ("SARRAFIYE.YARIM_YENI", -200, 400),
    ("SARRAFIYE.YARIM_ESKI", -200, 400),
    ("SARRAFIYE.TEK_YENI", -300, 600),
    ("SARRAFIYE.TEK_ESKI", -300, 600),
    ("SARRAFIYE.ATA_YENI", -200, 600),
    ("SARRAFIYE.ATA_ESKI", -200, 600),
    ("SARRAFIYE.ATA5_YENI", -1000, 1000),
    ("SARRAFIYE.GREMESE_YENI", -500, 1000),
    ("SARRAFIYE.GREMESE_ESKI", -500, 1000),
]


def upgrade() -> None:
    op.add_column(
        "margin_settings",
        sa.Column(
            "classic_alis_offset",
            sa.Numeric(12, 4),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "margin_settings",
        sa.Column(
            "classic_satis_offset",
            sa.Numeric(12, 4),
            nullable=False,
            server_default="0",
        ),
    )

    op.create_table(
        "pricing_config",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("mode", sa.String(16), nullable=False, server_default="milyem"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("id = 1", name="pricing_config_singleton"),
        sa.CheckConstraint("mode IN ('milyem','classic')", name="pricing_config_mode_check"),
    )
    op.execute("INSERT INTO pricing_config (id, mode) VALUES (1, 'milyem')")

    for sym, alis, satis in CLASSIC_DEFAULTS:
        op.execute(
            f"UPDATE margin_settings SET classic_alis_offset = {alis}, "
            f"classic_satis_offset = {satis} WHERE symbol_key = '{sym}'"
        )


def downgrade() -> None:
    op.drop_table("pricing_config")
    op.drop_column("margin_settings", "classic_satis_offset")
    op.drop_column("margin_settings", "classic_alis_offset")
