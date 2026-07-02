from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class PriceReference(BaseModel):
    ref_id: str = Field(description="Stable source id")
    description: str
    unit: str
    price: float = Field(gt=0)
    source: str = ""
    source_type: Literal["historical_bid", "catalogue", "estimate", "manual", "other"] = "other"
    observed_at: date | None = None
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class PriceStats(BaseModel):
    count: int
    min_price: float
    max_price: float
    median_price: float
    mean_price: float
    q1_price: float
    q3_price: float


class PriceSuggestion(BaseModel):
    price_low: int = Field(description="Lower suggested unit price in VND")
    price_high: int = Field(description="Upper suggested unit price in VND")
    unit: str = Field(default="", description="Unit of measure")
    currency: str = "VND"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning: str = Field(description="Short Vietnamese explanation")
    source_ids: list[str] = Field(default_factory=list)
    backend: str = ""
    warnings: list[str] = Field(default_factory=list)

    @field_validator("price_low", "price_high")
    @classmethod
    def positive_price(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("price must be positive")
        return value

    @model_validator(mode="after")
    def range_is_ordered(self) -> "PriceSuggestion":
        if self.price_low > self.price_high:
            self.price_low, self.price_high = self.price_high, self.price_low
        return self


class AdvisorRequest(BaseModel):
    description: str
    unit: str
    quantity: float | None = None
    top_k: int | None = None


class AdvisorError(BaseModel):
    error: str
    description: str = ""
    unit: str = ""
    reference_count: int = 0

