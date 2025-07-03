from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator, Field
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100, pattern="^[a-zA-Z0-9_]+$")
    full_name: Optional[str] = Field(None, max_length=200)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100, pattern="^[a-zA-Z0-9_]+$")
    full_name: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserInDB):
    pass


# Product Schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    category: Optional[str] = Field(None, max_length=100)
    sku: str = Field(..., min_length=1, max_length=100, pattern="^[A-Z0-9_-]+$")
    
    @validator('sku')
    def validate_sku(cls, v):
        if not v.isalnum() and not all(c in '_-' for c in v if not c.isalnum()):
            raise ValueError('SKU must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    category: Optional[str] = Field(None, max_length=100)
    # SKU is now optional and will be auto-generated
    sku: Optional[str] = Field(None, min_length=1, max_length=100, pattern="^[A-Z0-9_-]+$")
    
    @validator('sku')
    def validate_sku(cls, v):
        if v is not None:
            if not v.isalnum() and not all(c in '_-' for c in v if not c.isalnum()):
                raise ValueError('SKU must contain only alphanumeric characters, hyphens, and underscores')
            return v.upper()
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    # SKU cannot be updated after creation


class ProductInDB(ProductBase):
    id: int
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Product(ProductInDB):
    owner: User
    
    class Config:
        from_attributes = True


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Response Schemas
class Message(BaseModel):
    message: str


class PaginatedResponse(BaseModel):
    items: List[Product]
    total: int
    page: int
    size: int
    pages: int


# Login Schema
class Login(BaseModel):
    username: str
    password: str 