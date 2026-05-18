"""Gümüş Kg USD kaynağı SARRAFIYE.GUMUSUSD'ye geçer (Harem ile aynı)

Revision ID: 0013_gumus_usd_kg
Revises: 0012_kg_altin_usdkg
Create Date: 2026-05-18 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0013_gumus_usd_kg"
down_revision: Union[str, None] = "0012_kg_altin_usdkg"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Eski: COMPUTED.KG_GUMUS_USD = MADEN.XAGUSD × 32.1507 (spot ons × kg dönüşüm)
    # Yeni: SARRAFIYE.GUMUSUSD doğrudan ham USD/kg sarrafiye işlem fiyatı.
    # Kg Altın USD ile aynı pattern (migration 0012).
    op.execute(
        "UPDATE margin_settings SET symbol_key = 'SARRAFIYE.GUMUSUSD_RO' "
        "WHERE symbol_key = 'COMPUTED.KG_GUMUS_USD_RO'"
    )
    op.execute(
        "DELETE FROM daily_baselines "
        "WHERE symbol_key IN ('COMPUTED.KG_GUMUS_USD_RO', 'SARRAFIYE.GUMUSUSD_RO')"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE margin_settings SET symbol_key = 'COMPUTED.KG_GUMUS_USD_RO' "
        "WHERE symbol_key = 'SARRAFIYE.GUMUSUSD_RO'"
    )
    op.execute(
        "DELETE FROM daily_baselines "
        "WHERE symbol_key IN ('COMPUTED.KG_GUMUS_USD_RO', 'SARRAFIYE.GUMUSUSD_RO')"
    )
