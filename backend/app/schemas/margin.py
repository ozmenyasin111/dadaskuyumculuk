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
    classic_alis_offset: Decimal
    classic_satis_offset: Decimal
    sort_order: int
    is_readonly: bool
    is_multiplier: bool


class MarginUpdateIn(BaseModel):
    # Milyem değerleri (multiplier satırlarda milyem, diğerlerinde TL offset)
    alis_offset: Decimal
    satis_offset: Decimal
    # Classic (Fiyat Ekle/Çıkar) TL offset — sadece multiplier satırlarda anlamlı
    classic_alis_offset: Decimal | None = None
    classic_satis_offset: Decimal | None = None
