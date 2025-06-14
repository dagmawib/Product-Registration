from pydantic import BaseModel, Field, EmailStr
from datetime import date as datetime_date # Alias for clarity
from typing import Optional

class StoreCreate(BaseModel):
    storename: str
    email: EmailStr
    password: str # Restored
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

class AdminLogin(BaseModel): # Restored
    email: EmailStr
    password: str

class EmployeeLoginRequest(BaseModel): # New schema for employee login
    storename: str
    first_name: str
    last_name: str
    password: str

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    password: str # Restored
    phone_number: Optional[str] = None
    # store_id is removed, will be derived from admin current_user

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
    max_sell_price: float = Field(..., gt=0)
    date: datetime_date # Using aliased date
    store_id: int # This will be set by the endpoint using current_user.store_id
    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    purchase_price: Optional[float] = Field(default=None, gt=0)
    quantity: Optional[int] = Field(default=None, ge=0)
    max_sell_price: Optional[float] = Field(default=None, gt=0)
    date: Optional[datetime_date] = None # Corrected: Use alias and simple Optional for Pydantic v2

class ProductOut(ProductCreate):
    id: int
    net_profit: float
    min_sell_price: float
    class Config:
        from_attributes = True

class SaleCreate(BaseModel):
    product_id: int
    # user_id will be current_user.id, not from body
    # store_id will be current_user.store_id, not from body
    quantity: int
    timestamp: datetime_date # Using aliased date

class SaleOut(BaseModel): # Explicitly define all fields for SaleOut
    id: int
    product_id: int
    user_id: int
    store_id: int
    quantity: int
    timestamp: datetime_date # Using aliased date
    class Config:
        from_attributes = True
