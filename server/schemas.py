from pydantic import BaseModel, Field, conint, confloat
from datetime import date
from typing import Optional

class StoreCreate(BaseModel):
    name: str
    # For admin registration
    admin_username: str
    admin_password: str

class StoreOut(StoreCreate):
    id: int
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str
    role: str  # 'admin' or 'employee'
    store_id: Optional[int] = None  # Only required for employee creation
    store_name: Optional[str] = None  # Only for admin registration

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    store_id: int
    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    purchase_price: confloat(gt=0)
    quantity: conint(ge=0)
    sell_price: confloat(gt=0)
    max_sell_price: confloat(gt=0)
    date: date
    store_id: int

class ProductOut(ProductCreate):
    id: int
    net_profit: float
    min_sell_price: float

    class Config:
        from_attributes = True

class SaleCreate(BaseModel):
    product_id: int
    user_id: int
    quantity: int
    timestamp: date

class SaleOut(SaleCreate):
    id: int
    class Config:
        from_attributes = True
