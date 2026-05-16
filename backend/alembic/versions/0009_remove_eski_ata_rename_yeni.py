"""Eski Ata satırını kaldır, Yeni Ata → Ata (Cumhuriyet)

Revision ID: 0009_eski_ata_cumhuriyet
Revises: 0008_remove_aud_cad
Create Date: 2026-05-16 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0009_eski_ata_cumhuriyet"
down_revision: Union[str, None] = "0008_remove_aud_cad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DELETE FROM daily_baselines WHERE symbol_key = 'SARRAFIYE.ATA_ESKI'")
    op.execute("DELETE FROM margin_settings WHERE symbol_key = 'SARRAFIYE.ATA_ESKI'")
    op.execute(
        "UPDATE margin_settings SET display_name = 'Ata (Cumhuriyet)' "
        "WHERE symbol_key = 'SARRAFIYE.ATA_YENI'"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE margin_settings SET display_name = 'Yeni Ata' "
        "WHERE symbol_key = 'SARRAFIYE.ATA_YENI'"
    )
    op.execute(
        """
        INSERT INTO margin_settings
            (symbol_key, display_name, category, alis_offset, satis_offset,
             classic_alis_offset, classic_satis_offset, sort_order,
             is_readonly, is_multiplier)
        VALUES
            ('SARRAFIYE.ATA_ESKI', 'Eski Ata', 'ALTIN', 6.59, 6.72,
             -200, 600, 10, false, true)
        """
    )
