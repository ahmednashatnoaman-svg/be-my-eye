from __future__ import annotations

from pydantic import BaseModel, Field


class ProductInfo(BaseModel):
    name: str
    brand: str | None = None
    ingredients_text: str | None = None
    allergens: list[str] = Field(default_factory=list)


class ProductLookupRequest(BaseModel):
    barcode: str = Field(min_length=1)


class ProductLookupResponse(BaseModel):
    found: bool
    product: ProductInfo | None = None
