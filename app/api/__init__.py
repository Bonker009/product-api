from fastapi import APIRouter
from app.api import auth, products, users

api_router = APIRouter()

# Include all API routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(users.router, prefix="/users", tags=["users"]) 