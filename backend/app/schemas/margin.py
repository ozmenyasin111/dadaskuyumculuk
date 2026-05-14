from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class MarginOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol_key: str
    display_name: str
    category: str
    alis_offset: Decimal
    satis_offset: Decimal
    sort_order: int
    is_readonly: bool


class MarginUpdateIn(BaseModel):
    alis_offset: Decimal
    satis_offset: Decimal
