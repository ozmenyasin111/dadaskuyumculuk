"""Rename Has Altın → Gram Altın, fix döviz offset values

Revision ID: 0005_gram_altin
Revises: 0004_milyem
Create Date: 2026-05-15 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0005_gram_altin"
down_revision: Union[str, None] = "0004_milyem"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Has Altın → Gram Altın, offset -10/+40 → -15/+40
    op.execute("""
        UPDATE margin_settings
        SET display_name = 'Gram Altın',
            alis_offset = -15,
            satis_offset = 40
        WHERE symbol_key = 'MADEN.ALTIN'
    """)
    op.execute("""
        UPDATE margin_settings
        SET display_name = 'Gram Altın (Ham)'
        WHERE symbol_key = 'MADEN.ALTIN_RO'
    """)

    # Döviz offsetleri: ±0.15 → ±0.015 (EUR/USD dahil tüm döviz satırları)
    op.execute("""
        UPDATE margin_settings
        SET alis_offset = -0.015, satis_offset = 0.015
        WHERE category = 'DOVIZ'
          AND is_multiplier = false
          AND is_readonly = false
    """)

    # Offset değiştiği için ilgili baseline'ları sil — worker bir sonraki tick'te tazesini set eder
    op.execute("DELETE FROM daily_baselines WHERE symbol_key = 'MADEN.ALTIN'")
    op.execute("""
        DELETE FROM daily_baselines
        WHERE symbol_key IN (
            SELECT symbol_key FROM margin_settings
            WHERE category = 'DOVIZ' AND is_multiplier = false AND is_readonly = false
        )
    """)


def downgrade() -> None:
    op.execute("""
        UPDATE margin_settings
        SET display_name = 'Has Altın',
            alis_offset = -10,
            satis_offset = 40
        WHERE symbol_key = 'MADEN.ALTIN'
    """)
    op.execute("""
        UPDATE margin_settings
        SET display_name = 'Has Altın (Ham)'
        WHERE symbol_key = 'MADEN.ALTIN_RO'
    """)
    op.execute("""
        UPDATE margin_settings
        SET alis_offset = -0.15, satis_offset = 0.15
        WHERE category = 'DOVIZ'
          AND is_multiplier = false
          AND is_readonly = false
    """)
