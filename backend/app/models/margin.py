from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MarginSetting(Base):
    __tablename__ = "margin_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # API kaynak yolu, ör. "MADEN.ALTIN" veya "SARRAFIYE.AYAR22"; salt-okunur hesaplanan
    # satırlar için "COMPUTED.KG_ONS_ALTIN" gibi özel anahtarlar kullanılabilir.
    symbol_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)

    # "ALTIN" (sol kolon) | "DOVIZ" (sağ kolon) | "READONLY" (kuyumcu bakar paneli)
    category: Mapped[str] = mapped_column(String(32), nullable=False)

    # Milyem modu offset'leri.
    # is_multiplier=true satırlarda bunlar milyem (çarpan) değerleri olarak yorumlanır;
    # diğer satırlarda TL bazlı ekleme/çıkarma.
    alis_offset: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    satis_offset: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=0)

    # "Fiyat Ekle/Çıkar" (classic) modunda multiplier satırlar için TL bazlı offset.
    # Multiplier olmayan satırlarda kullanılmaz.
    classic_alis_offset: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    classic_satis_offset: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=0)

    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_readonly: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # True → satır milyem modunda Gram Altın display × milyem ile hesaplanır,
    # classic modunda kendi raw bid/ask + classic_*_offset kullanır.
    is_multiplier: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
