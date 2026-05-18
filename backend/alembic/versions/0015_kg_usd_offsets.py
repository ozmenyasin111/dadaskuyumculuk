"""Kg Altın USD / Gümüş Kg USD admin offset'leriyle editable

Revision ID: 0015_kg_usd_offsets
Revises: 0014_kg_parusd
Create Date: 2026-05-18 19:30:00.000000

Kuyumcu Paneli'ndeki Kg Altın USD ve Gümüş Kg USD satırları şimdiye
kadar readonly idi (offset yok, ham hesap). Kullanıcı bu iki satıra
default kâr marjı koymak istiyor:

  Kg Altın USD:   alış −50,  satış +50  USD
  Gümüş Kg USD:   alış −75,  satış +75  USD

is_readonly=false yapılınca processor offset path'ine girer ve değerler
ekranda uygulanır. category=READONLY kaldığı için ana sayfada hâlâ
Kuyumcu Paneli kısmında gösterilir (frontend kategori bazlı yerleştirme).
Admin/marjlar sayfasında bu satırlar "Gram Altın & Gümüş Kg (TL bazlı
kâr)" grubunda görünür ve kullanıcı offset'leri admin'den değiştirebilir.

Hem alis_offset/satis_offset (milyem mode için) hem classic_*_offset
(aktif classic mode için) aynı değerlerle dolduruluyor — mod değişse
bile davranış tutarlı kalır.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0015_kg_usd_offsets"
down_revision: Union[str, None] = "0014_kg_parusd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        UPDATE margin_settings
        SET is_readonly = false,
            alis_offset = -50, satis_offset = 50,
            classic_alis_offset = -50, classic_satis_offset = 50
        WHERE symbol_key = 'COMPUTED.KG_ALTIN_USD_RO'
    """)
    op.execute("""
        UPDATE margin_settings
        SET is_readonly = false,
            alis_offset = -75, satis_offset = 75,
            classic_alis_offset = -75, classic_satis_offset = 75
        WHERE symbol_key = 'COMPUTED.KG_GUMUS_USD_RO'
    """)
    # Offset değişikliği nedeniyle baseline temizliği
    op.execute(
        "DELETE FROM daily_baselines "
        "WHERE symbol_key IN ('COMPUTED.KG_ALTIN_USD_RO', 'COMPUTED.KG_GUMUS_USD_RO')"
    )


def downgrade() -> None:
    op.execute("""
        UPDATE margin_settings
        SET is_readonly = true,
            alis_offset = 0, satis_offset = 0,
            classic_alis_offset = 0, classic_satis_offset = 0
        WHERE symbol_key IN ('COMPUTED.KG_ALTIN_USD_RO', 'COMPUTED.KG_GUMUS_USD_RO')
    """)
    op.execute(
        "DELETE FROM daily_baselines "
        "WHERE symbol_key IN ('COMPUTED.KG_ALTIN_USD_RO', 'COMPUTED.KG_GUMUS_USD_RO')"
    )
