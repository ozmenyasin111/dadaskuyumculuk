"""gümüş satırını gram yerine kg cinsine çevir

Revision ID: 0003_gumus_kg
Revises: 0002_daily_baselines
Create Date: 2026-05-14 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0003_gumus_kg"
down_revision: Union[str, None] = "0002_daily_baselines"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        UPDATE margin_settings
        SET symbol_key = 'COMPUTED.KG_GUMUS_TL',
            display_name = 'Gümüş (Kg)',
            alis_offset = -200,
            satis_offset = 500
        WHERE symbol_key = 'SARRAFIYE.GUMUSTRY'
    """)
    op.execute("DELETE FROM daily_baselines WHERE symbol_key = 'SARRAFIYE.GUMUSTRY'")


def downgrade() -> None:
    op.execute("""
        UPDATE margin_settings
        SET symbol_key = 'SARRAFIYE.GUMUSTRY',
            display_name = 'Gümüş (Gram)',
            alis_offset = -0.2,
            satis_offset = 0.5
        WHERE symbol_key = 'COMPUTED.KG_GUMUS_TL'
    """)
    op.execute("DELETE FROM daily_baselines WHERE symbol_key = 'COMPUTED.KG_GUMUS_TL'")
