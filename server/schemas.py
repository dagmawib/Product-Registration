from pydantic import BaseModel, Field, conint, confloat, EmailStr
from datetime import date
from typing import Optional

class StoreCreate(BaseModel):
    storename: str
    email: EmailStr
    password: str
    phone_number: Optional[str] = None

class StoreOut(BaseModel):
    id: int
    storename: str
    email: EmailStr
    phone_number: Optional[str]
    class Config:
        from_attributes = True

class AdminOut(BaseModel):
    id: int
    email: EmailStr
    phone_number: Optional[str]
    storename: str
    role: str
    store_id: int
    class Config:
        from_attributes = True

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    password: str
    phone_number: Optional[str] = None

class EmployeeOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone_number: Optional[str]
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
