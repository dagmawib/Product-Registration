from pydantic import BaseModel, Field, conint, confloat
from datetime import date

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    purchase_price: confloat(gt=0)
    quantity: conint(ge=0)
    sell_price: confloat(gt=0)
    max_sell_price: confloat(gt=0)
    date: date

class ProductOut(ProductCreate):
    id: int
    net_profit: float
    min_sell_price: float

    class Config:
        orm_mode = True
