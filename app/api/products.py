from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_active_user, get_current_superuser
from app.crud import (
    get_product, get_products, create_product, update_product, delete_product,
    get_products_by_owner, get_product_statistics
)
from app.schemas import Product, ProductCreate, ProductUpdate, PaginatedResponse, Message
from app.models import User, Product as ProductModel

router = APIRouter()


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_new_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new product.
    
    - **name**: Product name (1-200 characters)
    - **description**: Optional product description
    - **price**: Product price (must be positive)
    - **stock_quantity**: Available stock (must be non-negative)
    - **category**: Optional product category
    - **sku**: Optional unique SKU code (auto-generated if not provided)
    """
    return create_product(db=db, product=product, owner_id=current_user.id)


@router.get("/", response_model=PaginatedResponse)
def read_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in name, description, or SKU"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    active_only: bool = Query(True, description="Show only active products"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve products with filtering and pagination.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Number of records to return (max 1000)
    - **category**: Filter by product category
    - **search**: Search in product name, description, or SKU
    - **min_price**: Filter by minimum price
    - **max_price**: Filter by maximum price
    - **active_only**: Show only active products
    """
    products = get_products(
        db=db,
        skip=skip,
        limit=limit,
        category=category,
        search=search,
        min_price=min_price,
        max_price=max_price,
        active_only=active_only
    )
    
    # Get total count for pagination
    total_products = len(get_products(
        db=db,
        category=category,
        search=search,
        min_price=min_price,
        max_price=max_price,
        active_only=active_only
    ))
    
    pages = (total_products + limit - 1) // limit
    page = (skip // limit) + 1
    
    return PaginatedResponse(
        items=products,
        total=total_products,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/my-products", response_model=PaginatedResponse)
def read_my_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve current user's products with pagination.
    """
    products = get_products_by_owner(
        db=db,
        owner_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    # Get total count for pagination
    total_products = len(get_products_by_owner(db=db, owner_id=current_user.id))
    
    pages = (total_products + limit - 1) // limit
    page = (skip // limit) + 1
    
    return PaginatedResponse(
        items=products,
        total=total_products,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/{product_id}", response_model=Product)
def read_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific product by ID.
    """
    product = get_product(db=db, product_id=product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.put("/{product_id}", response_model=Product)
def update_existing_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing product.
    
    Only the product owner or superuser can update the product.
    """
    return update_product(
        db=db,
        product_id=product_id,
        product_update=product_update,
        current_user=current_user
    )


@router.delete("/{product_id}", response_model=Message)
def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a product.
    
    Only the product owner or superuser can delete the product.
    """
    delete_product(db=db, product_id=product_id, current_user=current_user)
    return {"message": "Product deleted successfully"}


@router.get("/statistics/overview")
def get_overview_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get product statistics overview.
    """
    stats = get_product_statistics(db=db, owner_id=current_user.id)
    return stats


@router.get("/statistics/admin")
def get_admin_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get admin statistics for all products.
    Only accessible by superusers.
    """
    stats = get_product_statistics(db=db)
    return stats


@router.get("/categories/list")
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of all available product categories.
    """
    from sqlalchemy import distinct
    categories = db.query(distinct(ProductModel.category)).filter(
        ProductModel.category.isnot(None)
    ).all()
    return {"categories": [cat[0] for cat in categories if cat[0]]} 