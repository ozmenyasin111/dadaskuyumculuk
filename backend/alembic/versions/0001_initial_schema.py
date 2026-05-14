"""initial schema + seed defaults

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-14 00:00:00.000000

"""
from decimal import Decimal
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Default sembol haritası — Dadaş Kuyumculuk için. Admin panelden offset'ler değişir,
# ama satır seti burada sabit (yeni satır eklenirse yeni migration yazılır).
SOL_KOLON = [
    # (symbol_key,                display_name,        alis_offset, satis_offset)
    ("MADEN.ALTIN",               "Has Altın",         -20,         20),
    ("SARRAFIYE.AYAR22",          "Bilezik (22 Ayar)", -15,         100),
    ("SARRAFIYE.AYAR14",          "14 Ayar",           0,           700),
    ("SARRAFIYE.CEYREK_YENI",     "Yeni Çeyrek",       -100,        200),
    ("SARRAFIYE.CEYREK_ESKI",     "Eski Çeyrek",       -100,        200),
    ("SARRAFIYE.YARIM_YENI",      "Yeni Yarım",        -200,        400),
    ("SARRAFIYE.YARIM_ESKI",      "Eski Yarım",        -200,        400),
    ("SARRAFIYE.TEK_YENI",        "Yeni Tam",          -300,        600),
    ("SARRAFIYE.TEK_ESKI",        "Eski Tam",          -300,        600),
    ("SARRAFIYE.ATA_YENI",        "Yeni Ata",          -200,        600),
    ("SARRAFIYE.ATA_ESKI",        "Eski Ata",          -200,        600),
    ("SARRAFIYE.ATA5_YENI",       "Yeni Ata 5'li",     -1000,       1000),
    ("SARRAFIYE.ATA5_ESKI",       "Eski Ata 5'li",     -1000,       1000),
    ("SARRAFIYE.GREMESE_YENI",    "Yeni Gremse",       -500,        1000),
    ("SARRAFIYE.GREMESE_ESKI",    "Eski Gremse",       -500,        1000),
    ("SARRAFIYE.GUMUSTRY",        "Gümüş (Gram)",      Decimal("-0.2"), Decimal("0.5")),
]

SAG_KOLON = [
    ("DOVIZ.USDTRY",     "USD/TRY",  Decimal("-0.15"),   Decimal("0.15")),
    ("DOVIZ.EURTRY",     "EUR/TRY",  Decimal("-0.15"),   Decimal("0.15")),
    ("DOVIZ.EURUSDS",    "EUR/USD",  Decimal("-0.0015"), Decimal("0.0015")),
    ("DOVIZ.GBPTRY",     "GBP/TRY",  Decimal("-0.15"),   Decimal("0.15")),
    ("DOVIZ.CHFTRY",     "CHF/TRY",  Decimal("-0.15"),   Decimal("0.15")),
    ("DOVIZ.AUDTRY",     "AUD/TRY",  Decimal("-0.15"),   Decimal("0.15")),
    ("DOVIZ.CADTRY",     "CAD/TRY",  Decimal("-0.15"),   Decimal("0.15")),
    ("DOVIZ.SARTRY",     "SAR/TRY",  Decimal("-0.15"),   Decimal("0.15")),
]

# Salt-okunur "kuyumcu bakar" satırları — offset YOK.
READONLY = [
    ("MADEN.ALTIN",                "Has Altın (Ham)"),
    ("MADEN.XAUUSD",               "Ons Altın"),
    ("COMPUTED.KG_ONS_ALTIN",      "Kg Ons Altın"),
    ("MADEN.XAUXAG",               "Altın/Gümüş Rasyo"),
    ("MADEN.XAGUSD",               "Ons Gümüş"),
    ("MADEN.GUMUSD",               "Gümüş Kg USD"),
]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )

    margin_table = op.create_table(
        "margin_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol_key", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=64), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("alis_offset", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("satis_offset", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_readonly", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol_key"),
    )

    vol_table = op.create_table(
        "volatility_overrides",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("threshold", sa.Numeric(12, 4), nullable=False),
        sa.Column("alis_override", sa.Numeric(12, 4), nullable=False),
        sa.Column("satis_override", sa.Numeric(12, 4), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("category"),
    )

    # ---- Seed margin_settings ----
    rows = []
    sort = 0
    for sym, name, alis, satis in SOL_KOLON:
        rows.append(dict(
            symbol_key=sym, display_name=name, category="ALTIN",
            alis_offset=Decimal(alis), satis_offset=Decimal(satis),
            sort_order=sort, is_readonly=False,
        ))
        sort += 1

    sort = 0
    for sym, name, alis, satis in SAG_KOLON:
        rows.append(dict(
            symbol_key=sym, display_name=name, category="DOVIZ",
            alis_offset=Decimal(alis), satis_offset=Decimal(satis),
            sort_order=sort, is_readonly=False,
        ))
        sort += 1

    sort = 0
    for sym, name in READONLY:
        # NOT: symbol_key salt-okunurda unique olmak zorunda; READONLY için "_RO" eki kullanıyoruz
        # böylece aynı API path'i hem editable hem readonly olarak gözükebiliyor (Has Altın gibi).
        rows.append(dict(
            symbol_key=f"{sym}_RO",
            display_name=name, category="READONLY",
            alis_offset=Decimal(0), satis_offset=Decimal(0),
            sort_order=sort, is_readonly=True,
        ))
        sort += 1

    op.bulk_insert(margin_table, rows)

    # ---- Seed volatility_overrides ----
    op.bulk_insert(vol_table, [
        dict(category="ALTIN", threshold=Decimal(500), alis_override=Decimal(-200), satis_override=Decimal(300), enabled=True),
        dict(category="DOVIZ", threshold=Decimal(500), alis_override=Decimal(-100), satis_override=Decimal(200), enabled=True),
    ])


def downgrade() -> None:
    op.drop_table("volatility_overrides")
    op.drop_table("margin_settings")
    op.drop_table("users")
