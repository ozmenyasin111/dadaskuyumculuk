"""milyem (multiplier) bazlı fiyatlama — diğer altınlar Has Altın × milyem

Revision ID: 0004_milyem
Revises: 0003_gumus_kg
Create Date: 2026-05-14 04:00:00.000000

"""
from decimal import Decimal
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_milyem"
down_revision: Union[str, None] = "0003_gumus_kg"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (symbol_key, display_name, alis_milyem, satis_milyem)
MILYEM_ROWS = [
    ("SARRAFIYE.CEYREK_YENI", "Yeni Çeyrek", Decimal("1.62"), Decimal("1.6540")),
    ("SARRAFIYE.CEYREK_ESKI", "Eski Çeyrek", Decimal("1.5959"), Decimal("1.6440")),
    ("SARRAFIYE.YARIM_YENI", "Yeni Yarım", Decimal("3.24"), Decimal("3.3050")),
    ("SARRAFIYE.YARIM_ESKI", "Eski Yarım", Decimal("3.19"), Decimal("3.26")),
    ("SARRAFIYE.TEK_YENI", "Yeni Tam", Decimal("6.45"), Decimal("6.59")),
    ("SARRAFIYE.TEK_ESKI", "Eski Tam", Decimal("6.39"), Decimal("6.50")),
    ("SARRAFIYE.GREMESE_YENI", "Yeni Gremse", Decimal("16.12"), Decimal("16.60")),
    ("SARRAFIYE.GREMESE_ESKI", "Eski Gremse", Decimal("15.90"), Decimal("16.40")),
    ("SARRAFIYE.ATA_YENI", "Yeni Ata", Decimal("6.65"), Decimal("6.80")),
    ("SARRAFIYE.ATA_ESKI", "Eski Ata", Decimal("6.59"), Decimal("6.72")),
    ("SARRAFIYE.ATA5_YENI", "Ata 5'li", Decimal("33.00"), Decimal("33.85")),
    ("SARRAFIYE.AYAR14", "14 Ayar", Decimal("0.560"), Decimal("0.870")),
    ("SARRAFIYE.AYAR22", "Bilezik (22 Ayar)", Decimal("0.910"), Decimal("0.955")),
]


def upgrade() -> None:
    op.add_column(
        "margin_settings",
        sa.Column("is_multiplier", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    # Has Altın offset -20/+20 → -10/+40
    op.execute("UPDATE margin_settings SET alis_offset = -10, satis_offset = 40 WHERE symbol_key = 'MADEN.ALTIN'")

    # Ata 5'li: ESKI sil, YENI'yi tek "Ata 5'li" yap
    op.execute("DELETE FROM margin_settings WHERE symbol_key = 'SARRAFIYE.ATA5_ESKI'")
    op.execute("DELETE FROM daily_baselines WHERE symbol_key = 'SARRAFIYE.ATA5_ESKI'")

    # Sarrafiye altın satırlarını milyem moduna geçir
    for sym, name, alis_m, satis_m in MILYEM_ROWS:
        op.execute(
            f"UPDATE margin_settings SET is_multiplier = true, "
            f"alis_offset = {alis_m}, satis_offset = {satis_m}, "
            f"display_name = $${name}$$ "
            f"WHERE symbol_key = '{sym}'"
        )

    # Sıralama: Has Altın → Bilezik → 14 Ayar → Çeyrek → Yarım → Tam → Ata → Ata 5'li → Gremse → Gümüş
    order_map = [
        ("MADEN.ALTIN", 0),
        ("SARRAFIYE.AYAR22", 1),
        ("SARRAFIYE.AYAR14", 2),
        ("SARRAFIYE.CEYREK_YENI", 3),
        ("SARRAFIYE.CEYREK_ESKI", 4),
        ("SARRAFIYE.YARIM_YENI", 5),
        ("SARRAFIYE.YARIM_ESKI", 6),
        ("SARRAFIYE.TEK_YENI", 7),
        ("SARRAFIYE.TEK_ESKI", 8),
        ("SARRAFIYE.ATA_YENI", 9),
        ("SARRAFIYE.ATA_ESKI", 10),
        ("SARRAFIYE.ATA5_YENI", 11),
        ("SARRAFIYE.GREMESE_YENI", 12),
        ("SARRAFIYE.GREMESE_ESKI", 13),
        ("COMPUTED.KG_GUMUS_TL", 14),
    ]
    for sym, order in order_map:
        op.execute(f"UPDATE margin_settings SET sort_order = {order} WHERE symbol_key = '{sym}'")

    # Multiplier satırlarının baseline'larını sıfırla (hesap mantığı değişti)
    syms = "', '".join(s for s, _, _, _ in MILYEM_ROWS)
    op.execute(f"DELETE FROM daily_baselines WHERE symbol_key IN ('{syms}')")
    op.execute("DELETE FROM daily_baselines WHERE symbol_key = 'MADEN.ALTIN'")  # Has Altın offset değişti


def downgrade() -> None:
    op.execute("UPDATE margin_settings SET is_multiplier = false")
    op.execute("UPDATE margin_settings SET alis_offset = -20, satis_offset = 20 WHERE symbol_key = 'MADEN.ALTIN'")
    op.drop_column("margin_settings", "is_multiplier")
