from pydantic import BaseModel, Field, EmailStr
from datetime import date as datetime_date # Alias to avoid potential conflicts
from typing import Optional

class StoreCreate(BaseModel):
    storename: str
    email: EmailStr # Email for the primary contact/user of the store
    # password: str # Removed password
    phone_number: Optional[str] = None

class StoreOut(BaseModel):
    id: int
    storename: str
    email: EmailStr
    phone_number: Optional[str]
    class Config:
        from_attributes = True

class AdminOut(BaseModel): # This schema represents a user associated with a store
    id: int
    email: EmailStr
    phone_number: Optional[str]
    storename: str # Name of the store they are associated with
    role: str # Role, e.g., "admin"
    store_id: int
    class Config:
        from_attributes = True

# AdminLogin schema might be removed or repurposed if login is entirely gone.
# For now, let's assume it's not used.
# class AdminLogin(BaseModel):
#     email: EmailStr
#     password: str

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    # password: str # Removed password
    phone_number: Optional[str] = None
    store_id: int # Employee must be associated with a store, provided at creation

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
    purchase_price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    # sell_price: float = Field(..., gt=0)
    max_sell_price: float = Field(..., gt=0)
    date: datetime_date
    store_id: int

    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    purchase_price: Optional[float] = Field(default=None, gt=0)
    quantity: Optional[int] = Field(default=None, ge=0)
    # sell_price: Optional[float] = Field(default=None, gt=0)
    max_sell_price: Optional[float] = Field(default=None, gt=0)
    date: Optional[datetime_date] = None # Simplified: if no other Field params, default=None is implicit for Optional

class ProductOut(ProductCreate): # ProductOut inherits store_id and other fields from ProductCreate
    id: int
    net_profit: float
    min_sell_price: float
    # No need to redefine fields already in ProductCreate if they are the same
    class Config:
        from_attributes = True

class SaleCreate(BaseModel):
    product_id: int
    user_id: int # Represents the employee ID (or general user ID), to be provided in request
    store_id: int # Represents the store ID, to be provided in request
    quantity: int
    timestamp: datetime_date

class SaleOut(SaleCreate):
    id: int
    class Config:
        from_attributes = True
