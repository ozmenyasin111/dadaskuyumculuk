"""ATA (Cumhuriyet) karma sembole geçer — alış ATA_ESKI bid'inden, satış ATA_YENI ask'ından

Revision ID: 0010_ata_composite
Revises: 0009_eski_ata_cumhuriyet
Create Date: 2026-05-16 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0010_ata_composite"
down_revision: Union[str, None] = "0009_eski_ata_cumhuriyet"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SARRAFIYE.ATA_YENI → COMPUTED.ATA_CUMHURIYET (karma sembol).
    # symbol_map._compute() bu sembolü gördüğünde:
    #   bid  = ATA_ESKI.bid   (API'den)
    #   ask  = ATA_YENI.ask   (API'den)
    op.execute(
        "UPDATE margin_settings SET symbol_key = 'COMPUTED.ATA_CUMHURIYET' "
        "WHERE symbol_key = 'SARRAFIYE.ATA_YENI'"
    )
    # Baseline temizle, raw kaynak değiştiği için yeniden yazılsın
    op.execute(
        "DELETE FROM daily_baselines "
        "WHERE symbol_key IN ('SARRAFIYE.ATA_YENI', 'COMPUTED.ATA_CUMHURIYET')"
    )


def downgrade() -> None:
    op.execute(
        "UPDATE margin_settings SET symbol_key = 'SARRAFIYE.ATA_YENI' "
        "WHERE symbol_key = 'COMPUTED.ATA_CUMHURIYET'"
    )
    op.execute(
        "DELETE FROM daily_baselines "
        "WHERE symbol_key IN ('SARRAFIYE.ATA_YENI', 'COMPUTED.ATA_CUMHURIYET')"
    )
