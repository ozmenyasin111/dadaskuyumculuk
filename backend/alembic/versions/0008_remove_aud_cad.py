"""AUD/TRY ve CAD/TRY satırlarını kaldır

Revision ID: 0008_remove_aud_cad
Revises: 0007_pricing_mode
Create Date: 2026-05-16 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0008_remove_aud_cad"
down_revision: Union[str, None] = "0007_pricing_mode"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "DELETE FROM daily_baselines WHERE symbol_key IN ('DOVIZ.AUDTRY', 'DOVIZ.CADTRY')"
    )
    op.execute(
        "DELETE FROM margin_settings WHERE symbol_key IN ('DOVIZ.AUDTRY', 'DOVIZ.CADTRY')"
    )


def downgrade() -> None:
    op.execute(
        """
        INSERT INTO margin_settings
            (symbol_key, display_name, category, alis_offset, satis_offset,
             classic_alis_offset, classic_satis_offset, sort_order,
             is_readonly, is_multiplier)
        VALUES
            ('DOVIZ.AUDTRY', 'AUD/TRY', 'DOVIZ', -0.015, 0.015, 0, 0, 5, false, false),
            ('DOVIZ.CADTRY', 'CAD/TRY', 'DOVIZ', -0.015, 0.015, 0, 0, 6, false, false)
        """
    )
