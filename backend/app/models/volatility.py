from decimal import Decimal

from sqlalchemy import Boolean, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class VolatilityOverride(Base):
    __tablename__ = "volatility_overrides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # "ALTIN" veya "DOVIZ" — Has Altın için ALTIN kuralı uygulanır, tüm döviz sembolleri
    # için DOVIZ kuralı uygulanır.
    category: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)

    threshold: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    alis_override: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    satis_override: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)

    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
