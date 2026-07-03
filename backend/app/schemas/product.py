from __future__ import annotations

from pydantic import BaseModel, Field


class ProductInfo(BaseModel):
    name: str
    brand: str | None = None
    ingredients_text: str | None = None
    allergens: list[str] = Field(default_factory=list)


class ProductLookupRequest(BaseModel):
    # GTIN/EAN/UPC barcodes are numeric, 6-14 digits. Restricting the pattern
    # here (rather than accepting any string) prevents a barcode value from
    # being used to inject path/query segments into the Open Food Facts URL.
    barcode: str = Field(min_length=6, max_length=14, pattern=r"^[0-9]+$")


class ProductLookupResponse(BaseModel):
    found: bool
    product: ProductInfo | None = None
