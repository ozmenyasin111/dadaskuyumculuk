from typing import Literal

from pydantic import BaseModel, ConfigDict


class PricingModeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mode: Literal["milyem", "classic"]


class PricingModeUpdateIn(BaseModel):
    mode: Literal["milyem", "classic"]
