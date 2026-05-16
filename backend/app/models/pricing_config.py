from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PricingConfig(Base):
    """Tek satırlı (id=1) global fiyatlandırma modu seçimi.

    `mode`:
      - `milyem`   → Multiplier satırlar Gram Altın × milyem ile hesaplanır
      - `classic`  → Multiplier satırlar API'deki kendi raw bid/ask + classic offset
    """

    __tablename__ = "pricing_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    mode: Mapped[str] = mapped_column(String(16), nullable=False, default="milyem")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
