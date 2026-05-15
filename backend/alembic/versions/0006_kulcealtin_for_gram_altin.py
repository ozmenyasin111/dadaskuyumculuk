"""Sarrafiye Gram Altın → SARRAFIYE.KULCEALTIN kaynağı; Kuyumcu Paneli Has Altın (Ham)

Revision ID: 0006_kulcealtin
Revises: 0005_gram_altin
Create Date: 2026-05-15 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0006_kulcealtin"
down_revision: Union[str, None] = "0005_gram_altin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Sarrafiye'deki "Gram Altın" satırı (eski MADEN.ALTIN) artık SARRAFIYE.KULCEALTIN
    # üzerinden çalışsın — Harem'in "GRAM ALTIN" satırının kaynağı bu sembol.
    op.execute("""
        UPDATE margin_settings
        SET symbol_key = 'SARRAFIYE.KULCEALTIN'
        WHERE symbol_key = 'MADEN.ALTIN' AND is_readonly = false
    """)

    # Kuyumcu Paneli readonly satırı yeniden "Has Altın (Ham)" — kaynak MADEN.ALTIN aynen kalır.
    op.execute("""
        UPDATE margin_settings
        SET display_name = 'Has Altın (Ham)'
        WHERE symbol_key = 'MADEN.ALTIN_RO'
    """)

    # Hesap kaynağı değiştiği için ilgili tüm baseline'ları temizle — worker bir sonraki
    # tick'te tazesini yazar (milyem satırları da referansı değiştiği için etkilenir).
    op.execute("""
        DELETE FROM daily_baselines
        WHERE symbol_key IN ('MADEN.ALTIN', 'SARRAFIYE.KULCEALTIN')
           OR symbol_key IN (
               SELECT symbol_key FROM margin_settings WHERE is_multiplier = true
           )
    """)


def downgrade() -> None:
    op.execute("""
        UPDATE margin_settings
        SET symbol_key = 'MADEN.ALTIN'
        WHERE symbol_key = 'SARRAFIYE.KULCEALTIN' AND is_readonly = false
    """)
    op.execute("""
        UPDATE margin_settings
        SET display_name = 'Gram Altın (Ham)'
        WHERE symbol_key = 'MADEN.ALTIN_RO'
    """)
