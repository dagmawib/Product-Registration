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

# Schema for JWT Token response
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None # Subject (e.g., username or email)
    role: Optional[str] = None
    id: Optional[int] = None # User ID

# Schema for initial Admin and Store Registration
class AdminStoreRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    phone_number: Optional[str] = None
    store_name: str = Field(..., min_length=1)
    # You can add more fields here if needed for store or admin during initial setup
    # e.g., store_address: Optional[str] = None

# User Schemas (generic for User model)
class UserBase(BaseModel):
    email: EmailStr
    store_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: str = Field(default="employee") # Default role

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    store_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    # Role and password updates should be handled by specific endpoints/logic

class UserResponse(UserBase):
    id: int
    is_active: bool = True # Assuming you might add an is_active field to your model

    class Config:
        from_attributes = True

# Product Schemas (redefined for clarity and consistency with User model)
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    purchase_price: float = Field(..., gt=0)
    quantity_available: int = Field(..., ge=0) # Renamed from quantity for clarity
    # max_sell_price: float = Field(..., gt=0) # Consider if this is still needed or derived
    # date: datetime_date # Date added, could be auto-set

class ProductCreate(ProductBase):
    # added_by_user_id will be set by the endpoint
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    purchase_price: Optional[float] = Field(default=None, gt=0)
    quantity_available: Optional[int] = Field(default=None, ge=0)
    # max_sell_price: Optional[float] = Field(default=None, gt=0)

class ProductResponse(ProductBase):
    id: int
    added_by_user_id: int
    date_added: datetime_date # Assuming your model has this
    # net_profit: Optional[float] = None # This would be a calculated field, maybe not directly in DB model schema
    # min_sell_price: Optional[float] = None # Also likely calculated

    class Config:
        from_attributes = True

# SoldProduct Schemas (redefined for clarity)
class SoldProductBase(BaseModel):
    product_id: int
    quantity_sold: int = Field(..., gt=0)
    sale_price: float = Field(..., gt=0) # Price per unit at which it was sold
    date_sold: Optional[datetime_date] = None # Can default to now in the endpoint

class SoldProductCreate(SoldProductBase):
    # sold_by_user_id will be set by the endpoint
    pass

class SoldProductUpdate(BaseModel):
    quantity_sold: Optional[int] = Field(default=None, gt=0)
    sale_price: Optional[float] = Field(default=None, gt=0)
    date_sold: Optional[datetime_date] = None

class SoldProductResponse(SoldProductBase):
    id: int
    sold_by_user_id: int
    date_sold: datetime_date # Ensure this is not optional for response

    class Config:
        from_attributes = True

# Dashboard Metrics Schema
class DashboardMetrics(BaseModel):
    total_products: int
    total_sales_volume: float
    total_units_sold: int
    total_employees: int
    # Add other metrics as needed
