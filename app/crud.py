from typing import List, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
import uuid
import re
from app.models import User, Product
from app.schemas import UserCreate, UserUpdate, ProductCreate, ProductUpdate
from app.auth import get_password_hash


# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get list of users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """Create new user."""
    # Check if email already exists
    if get_user_by_email(db, email=user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if get_user_by_username(db, username=user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user information."""
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    update_data = user_update.dict(exclude_unset=True)
    
    # Check for email uniqueness if updating email
    if "email" in update_data:
        existing_user = get_user_by_email(db, email=update_data["email"])
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Check for username uniqueness if updating username
    if "username" in update_data:
        existing_user = get_user_by_username(db, username=update_data["username"])
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete user."""
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(db_user)
    db.commit()
    return True


# Product CRUD operations
def get_product(db: Session, product_id: int) -> Optional[Product]:
    """Get product by ID."""
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
    """Get product by SKU."""
    return db.query(Product).filter(Product.sku == sku.upper()).first()


def get_products(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    active_only: bool = True
) -> List[Product]:
    """Get list of products with filtering and pagination."""
    query = db.query(Product)
    
    # Apply filters
    if active_only:
        query = query.filter(Product.is_active == True)
    
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        search_filter = or_(
            Product.name.ilike(f"%{search}%"),
            Product.description.ilike(f"%{search}%"),
            Product.sku.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    return query.offset(skip).limit(limit).all()


def get_products_by_owner(
    db: Session, 
    owner_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[Product]:
    """Get products by owner."""
    return db.query(Product).filter(
        Product.owner_id == owner_id
    ).offset(skip).limit(limit).all()


def generate_unique_sku(db: Session, base_name: str = None) -> str:
    """Generate a unique SKU based on product name or random UUID."""
    if base_name:
        # Create SKU from product name: remove special chars, uppercase, limit length
        clean_name = re.sub(r'[^A-Za-z0-9]', '', base_name).upper()
        clean_name = clean_name[:8]  # Limit to 8 characters
        if not clean_name:
            clean_name = "PROD"
        
        # Try with base name first
        counter = 1
        while True:
            sku = f"{clean_name}-{counter:04d}"
            if not get_product_by_sku(db, sku):
                return sku
            counter += 1
            if counter > 9999:  # Fallback to UUID if too many attempts
                break
    else:
        # Fallback to UUID-based SKU
        clean_name = "PROD"
    
    # Generate UUID-based SKU
    while True:
        uuid_part = str(uuid.uuid4()).replace('-', '')[:8].upper()
        sku = f"{clean_name}-{uuid_part}"
        if not get_product_by_sku(db, sku):
            return sku


def create_product(db: Session, product: ProductCreate, owner_id: int) -> Product:
    """Create new product."""
    product_data = product.dict()
    
    # Auto-generate SKU if not provided
    if not product_data.get("sku"):
        product_data["sku"] = generate_unique_sku(db, product_data.get("name"))
    else:
        # Check if provided SKU already exists
        if get_product_by_sku(db, sku=product_data["sku"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU already exists"
            )
    
    db_product = Product(
        **product_data,
        owner_id=owner_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(
    db: Session, 
    product_id: int, 
    product_update: ProductUpdate,
    current_user: User
) -> Optional[Product]:
    """Update product information."""
    db_product = get_product(db, product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check ownership or superuser permissions
    if db_product.owner_id != current_user.id and not bool(current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this product"
        )
    
    update_data = product_update.dict(exclude_unset=True)
    
    # SKU cannot be updated after creation
    if "sku" in update_data:
        del update_data["sku"]
    
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int, current_user: User) -> bool:
    """Delete product."""
    db_product = get_product(db, product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check ownership or superuser permissions
    if db_product.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this product"
        )
    
    db.delete(db_product)
    db.commit()
    return True


def get_product_statistics(db: Session, owner_id: Optional[int] = None) -> dict:
    """Get product statistics."""
    query = db.query(Product)
    
    if owner_id:
        query = query.filter(Product.owner_id == owner_id)
    
    total_products = query.count()
    active_products = query.filter(Product.is_active == True).count()
    total_value = query.with_entities(func.sum(Product.price * Product.stock_quantity)).scalar() or 0
    
    return {
        "total_products": total_products,
        "active_products": active_products,
        "inactive_products": total_products - active_products,
        "total_value": float(total_value)
    } 