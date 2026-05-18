"""Kg Altın USD kaynağı SARRAFIYE.USDKG'ye geçer (Harem ile aynı)

Revision ID: 0012_kg_altin_usdkg
Revises: 0011_kg_gumus_usd
Create Date: 2026-05-18 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0012_kg_altin_usdkg"
down_revision: Union[str, None] = "0011_kg_gumus_usd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Eski formül: COMPUTED.KG_ONS_ALTIN = MADEN.XAUUSD × 32.1507 (spot oz × kg dönüşüm).
    # Sarrafiye işlem fiyatından ~1000 TL farklı çıkıyordu, Harem'in gösterdiği
    # değer SARRAFIYE.USDKG ham verisidir. Doğrudan oradan çekiyoruz, hesap yok.
    op.execute(
        "UPDATE margin_settings SET symbol_key = 'SARRAFIYE.USDKG_RO' "
        "WHERE symbol_key = 'COMPUTED.KG_ONS_ALTIN_RO'"
    )
    op.execute(
        "DELETE FROM daily_baselines "
        "WHERE symbol_key IN ('COMPUTED.KG_ONS_ALTIN_RO', 'SARRAFIYE.USDKG_RO')"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE margin_settings SET symbol_key = 'COMPUTED.KG_ONS_ALTIN_RO' "
        "WHERE symbol_key = 'SARRAFIYE.USDKG_RO'"
    )
    op.execute(
        "DELETE FROM daily_baselines "
        "WHERE symbol_key IN ('COMPUTED.KG_ONS_ALTIN_RO', 'SARRAFIYE.USDKG_RO')"
    )
