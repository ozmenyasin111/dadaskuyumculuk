"""Gümüş Kg USD'i COMPUTED.KG_GUMUS_USD'ye taşı; Kg Ons Altın → 'Kg Altın USD' adlandırması

Revision ID: 0011_kg_gumus_usd
Revises: 0010_ata_composite
Create Date: 2026-05-16 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0011_kg_gumus_usd"
down_revision: Union[str, None] = "0010_ata_composite"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # MADEN.GUMUSD ham değeri USD/gram. Eskiden "Gümüş Kg USD" diyerek doğrudan
    # gösteriyorduk, ekrana ~2.28 USD gibi anlamsız bir değer çıkıyordu.
    # COMPUTED.KG_GUMUS_USD: XAGUSD (USD/oz) × 32.1507 = doğru USD/kg.
    op.execute(
        "UPDATE margin_settings SET symbol_key = 'COMPUTED.KG_GUMUS_USD_RO' "
        "WHERE symbol_key = 'MADEN.GUMUSD_RO'"
    )
    op.execute(
        "DELETE FROM daily_baselines "
        "WHERE symbol_key IN ('MADEN.GUMUSD_RO', 'COMPUTED.KG_GUMUS_USD_RO')"
    )
    # "Kg Ons Altın" ismi kafa karıştırıcı (sayı USD/kg, ons değil).
    op.execute(
        "UPDATE margin_settings SET display_name = 'Kg Altın USD' "
        "WHERE symbol_key = 'COMPUTED.KG_ONS_ALTIN_RO'"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE margin_settings SET symbol_key = 'MADEN.GUMUSD_RO' "
        "WHERE symbol_key = 'COMPUTED.KG_GUMUS_USD_RO'"
    )
    op.execute(
        "DELETE FROM daily_baselines "
        "WHERE symbol_key IN ('MADEN.GUMUSD_RO', 'COMPUTED.KG_GUMUS_USD_RO')"
    )
    op.execute(
        "UPDATE margin_settings SET display_name = 'Kg Ons Altın' "
        "WHERE symbol_key = 'COMPUTED.KG_ONS_ALTIN_RO'"
    )
