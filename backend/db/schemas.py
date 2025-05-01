# db/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# For user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Token response (with extended expiration using our token creation logic)
class Token(BaseModel):
    access_token: str
    token_type: str


# User Schemas

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Upload Schemas
class UploadBase(BaseModel):
    file_name: str

class UploadCreate(UploadBase):
    pass

class UploadOut(UploadBase):
    id: int  # This should be the unique identifier for the upload
    file_path: str
    file_size: int
    uploaded_at: datetime
    status: str
    job_id: Optional[str] = None  # Redis job ID (Optional)
    upload_id: int  # Mapping to the primary `id` of the upload record (Database ID)

    class Config:
        from_attributes = True

# Response schema for historical uploads
class UploadHistoryResponse(BaseModel):
    uploads: List[UploadOut]
    message: Optional[str] = None


# LineItem Schemas
class LineItemBase(BaseModel):
    lineitem_quantity: Optional[int]
    lineitem_name: Optional[str]
    lineitem_price: Optional[float]  # Changed from str to float
    lineitem_compare_at_price: Optional[float]  # Changed from str to float
    lineitem_sku: Optional[str]
    lineitem_requires_shipping: Optional[str]
    lineitem_taxable: Optional[str]
    lineitem_fulfillment_status: Optional[str]
    lineitem_discount: Optional[float]  # Changed from str to float
    variant_id: Optional[str]

class LineItemOut(LineItemBase):
    id: int

    class Config:
        from_attributes = True

# Order Schemas
class OrderBase(BaseModel):
    name: str
    email: EmailStr
    financial_status: Optional[str]
    total: Optional[float]  # Changed from str to float
    order_id: Optional[str]

class OrderOut(OrderBase):
    id: int
    line_items: List[LineItemOut] = []

    class Config:
        from_attributes = True

# For decoding JWT token data (if needed)
class TokenData(BaseModel):
    user_id: Optional[int] = None
