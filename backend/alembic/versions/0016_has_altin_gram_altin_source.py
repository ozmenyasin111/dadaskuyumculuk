"""Kuyumcu Paneli "Has Altın (Ham)" kaynağını MADEN.ALTIN_RO → GRAM ALTIN.ALTIN_RO

Neden: finansveri'nin DS_ sembol geçişiyle birlikte eski `MADEN.ALTIN` sembolü
donmaya başladı (gün içinde 14:40'ta kalıp güncellenmedi), oysa "GRAM ALTIN.ALTIN"
canlı tıklıyor. Has Altın satırı salt-okunur kalır (marj eklenmez), sadece canlı
kaynaktan beslenir.

Revision ID: 0016_has_altin_gram
Revises: 0015_kg_usd_offsets
Create Date: 2026-06-29 20:45:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0016_has_altin_gram"
down_revision: Union[str, None] = "0015_kg_usd_offsets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Has Altın (Ham) readonly satırı artık canlı "GRAM ALTIN.ALTIN" sembolünü okur.
    op.execute("""
        UPDATE margin_settings
        SET symbol_key = 'GRAM ALTIN.ALTIN_RO'
        WHERE symbol_key = 'MADEN.ALTIN_RO'
    """)

    # Kaynak sembol değişti → eski baseline'ı temizle, worker bir sonraki tick'te
    # tazesini yazar (trend/yüzde doğru hesaplansın).
    op.execute("""
        DELETE FROM daily_baselines
        WHERE symbol_key IN ('MADEN.ALTIN_RO', 'GRAM ALTIN.ALTIN_RO')
    """)


def downgrade() -> None:
    op.execute("""
        UPDATE margin_settings
        SET symbol_key = 'MADEN.ALTIN_RO'
        WHERE symbol_key = 'GRAM ALTIN.ALTIN_RO'
    """)
    op.execute("""
        DELETE FROM daily_baselines
        WHERE symbol_key IN ('MADEN.ALTIN_RO', 'GRAM ALTIN.ALTIN_RO')
    """)
