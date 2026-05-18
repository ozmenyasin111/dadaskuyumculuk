"""Kg Altın USD ve Gümüş Kg USD kaynaklarını PARUSD/GUMUSD × 1000'e geçir

Revision ID: 0014_kg_parusd
Revises: 0013_gumus_usd_kg
Create Date: 2026-05-18 19:15:00.000000

api.finansveri.com sağlayıcısının teyidiyle: Harem altın "Kg Altın USD"
değerini MADEN.PARUSD'den (USD/gr Türk sarrafiye altın) × 1000 ile
hesaplayarak gösteriyor. Bizim önceden bağlandığımız SARRAFIYE.USDKG
sembolü 13 gündür donuk olduğu için bu yola geçiyoruz.

Gümüş için aynı pattern: MADEN.GUMUSD × 1000 — kullanıcının anlık
karşılaştırmasıyla Harem değeriyle <3 USD fark doğrulandı.

Yeni hesaplı semboller symbol_map._compute içinde tanımlı:
  COMPUTED.KG_ALTIN_USD → MADEN.PARUSD × 1000
  COMPUTED.KG_GUMUS_USD → MADEN.GUMUSD × 1000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0014_kg_parusd"
down_revision: Union[str, None] = "0013_gumus_usd_kg"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE margin_settings SET symbol_key = 'COMPUTED.KG_ALTIN_USD_RO' "
        "WHERE symbol_key = 'SARRAFIYE.USDKG_RO'"
    )
    op.execute(
        "UPDATE margin_settings SET symbol_key = 'COMPUTED.KG_GUMUS_USD_RO' "
        "WHERE symbol_key = 'SARRAFIYE.GUMUSUSD_RO'"
    )
    # Baseline temizliği — yeni kaynaktan tazesi yazılsın
    op.execute(
        "DELETE FROM daily_baselines WHERE symbol_key IN ("
        "'SARRAFIYE.USDKG_RO', 'COMPUTED.KG_ALTIN_USD_RO',"
        "'SARRAFIYE.GUMUSUSD_RO', 'COMPUTED.KG_GUMUS_USD_RO'"
        ")"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE margin_settings SET symbol_key = 'SARRAFIYE.USDKG_RO' "
        "WHERE symbol_key = 'COMPUTED.KG_ALTIN_USD_RO'"
    )
    op.execute(
        "UPDATE margin_settings SET symbol_key = 'SARRAFIYE.GUMUSUSD_RO' "
        "WHERE symbol_key = 'COMPUTED.KG_GUMUS_USD_RO'"
    )
    op.execute(
        "DELETE FROM daily_baselines WHERE symbol_key IN ("
        "'SARRAFIYE.USDKG_RO', 'COMPUTED.KG_ALTIN_USD_RO',"
        "'SARRAFIYE.GUMUSUSD_RO', 'COMPUTED.KG_GUMUS_USD_RO'"
        ")"
    )
