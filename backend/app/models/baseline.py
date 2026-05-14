from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DailyBaseline(Base):
    __tablename__ = "daily_baselines"

    symbol_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    baseline_date: Mapped[date] = mapped_column(Date, nullable=False)
    baseline_alis: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
