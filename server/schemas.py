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
    first_name: Optional[str] # Added first_name
    last_name: Optional[str]  # Added last_name
    phone_number: Optional[str]
    store_name: str  # Changed from storename to store_name for consistency
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
    sub: Optional[str] = None # Subject (e.g., username, email, or id)
    role: Optional[str] = None
    store_id: Optional[int] = None # Include store_id in token data

# Schema for initial Admin and Store Registration
class AdminStoreRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1) # Added first_name
    last_name: str = Field(..., min_length=1)  # Added last_name
    phone_number: Optional[str] = None
    store_name: str = Field(..., min_length=1)

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

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1)
    last_name: Optional[str] = Field(default=None, min_length=1)
    phone_number: Optional[str] = None
    # Password should be updated via a separate, dedicated endpoint for security reasons
    # Role and store_id should generally not be updated via a generic user update endpoint

class DashboardMetrics(BaseModel):
    total_products: int
    total_sales_value: float
    total_sold_items: int
    # Potentially add more complex fields like:
    # top_selling_products: List[ProductOut] # Or a simplified version
    # sales_over_time: Dict[str, float] # e.g., sales per day/month
    class Config:
        from_attributes = True
