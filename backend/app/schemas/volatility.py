from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class VolatilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    threshold: Decimal
    alis_override: Decimal
    satis_override: Decimal
    enabled: bool


class VolatilityUpdateIn(BaseModel):
    threshold: Decimal
    alis_override: Decimal
    satis_override: Decimal
    enabled: bool
