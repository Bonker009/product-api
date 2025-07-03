#!/usr/bin/env python3
"""
Database initialization script for the Product Management API.
This script creates the database tables and optionally creates a superuser.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from app.database import create_tables, SessionLocal
from app.models import User, Product
from app.auth import get_password_hash
from app.config import settings
from datetime import datetime

def create_superuser():
    """Create a superuser for testing."""
    db = SessionLocal()
    try:
        # Check if superuser already exists
        existing_superuser = db.query(User).filter(User.is_superuser == True).first()
        if existing_superuser:
            print(f"✅ Superuser already exists: {existing_superuser.username}")
            return existing_superuser
        
        # Create superuser
        superuser_data = {
            "email": "admin@example.com",
            "username": "admin",
            "hashed_password": get_password_hash("AdminPass123"),
            "full_name": "System Administrator",
            "is_active": True,
            "is_superuser": True
        }
        
        superuser = User(**superuser_data)
        db.add(superuser)
        db.commit()
        db.refresh(superuser)
        
        print("✅ Superuser created successfully!")
        print(f"   Username: {superuser.username}")
        print(f"   Email: {superuser.email}")
        print(f"   Password: AdminPass123")
        print("   ⚠️  Remember to change the password in production!")
        
        return superuser
        
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def create_sample_data():
    """Create sample data for testing."""
    db = SessionLocal()
    try:
        # Create a regular user
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "hashed_password": get_password_hash("UserPass123"),
            "full_name": "Test User",
            "is_active": True,
            "is_superuser": False
        }
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if existing_user:
            print(f"✅ Test user already exists: {existing_user.username}")
            return existing_user
        
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print("✅ Test user created successfully!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Password: UserPass123")
        
        return user
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def create_sample_products():
    """Create sample products for testing."""
    db = SessionLocal()
    try:
        # Check if products already exist
        existing_products = db.query(Product).count()
        if existing_products > 0:
            print(f"✅ Sample products already exist ({existing_products} products)")
            return existing_products
        
        # Get admin user as owner
        admin_user = db.query(User).filter(User.is_superuser == True).first()
        if not admin_user:
            print("❌ No admin user found. Please create a superuser first.")
            return 0
        
        # Sample product data
        sample_products = [
            {
                "name": "iPhone 15 Pro",
                "description": "Latest iPhone with A17 Pro chip, titanium design, and advanced camera system",
                "price": 999.99,
                "stock_quantity": 50,
                "category": "Electronics",
                "sku": "IPH15PRO-001"
            },
            {
                "name": "MacBook Air M2",
                "description": "Ultra-thin laptop with Apple M2 chip, perfect for productivity and creativity",
                "price": 1199.99,
                "stock_quantity": 25,
                "category": "Electronics",
                "sku": "MBA-M2-001"
            },
            {
                "name": "Nike Air Max 270",
                "description": "Comfortable running shoes with Air Max technology for maximum cushioning",
                "price": 150.00,
                "stock_quantity": 100,
                "category": "Sports",
                "sku": "NIKE-AM270-001"
            },
            {
                "name": "Samsung 4K Smart TV",
                "description": "55-inch 4K Ultra HD Smart TV with Crystal Display and Alexa Built-in",
                "price": 699.99,
                "stock_quantity": 15,
                "category": "Electronics",
                "sku": "SAMS-4K55-001"
            },
            {
                "name": "Coffee Maker Deluxe",
                "description": "Programmable coffee maker with 12-cup capacity and auto-shutoff",
                "price": 89.99,
                "stock_quantity": 75,
                "category": "Home & Kitchen",
                "sku": "COFF-DELUX-001"
            },
            {
                "name": "Wireless Bluetooth Headphones",
                "description": "Noise-cancelling wireless headphones with 30-hour battery life",
                "price": 199.99,
                "stock_quantity": 60,
                "category": "Electronics",
                "sku": "BT-HP-001"
            },
            {
                "name": "Yoga Mat Premium",
                "description": "Non-slip yoga mat made from eco-friendly materials, perfect for home workouts",
                "price": 45.00,
                "stock_quantity": 200,
                "category": "Sports",
                "sku": "YOGA-MAT-001"
            },
            {
                "name": "Kitchen Knife Set",
                "description": "Professional 8-piece knife set with wooden block and sharpener",
                "price": 129.99,
                "stock_quantity": 40,
                "category": "Home & Kitchen",
                "sku": "KNIFE-SET-001"
            },
            {
                "name": "Gaming Mouse RGB",
                "description": "High-precision gaming mouse with customizable RGB lighting and 6 programmable buttons",
                "price": 79.99,
                "stock_quantity": 80,
                "category": "Electronics",
                "sku": "GAME-MOUSE-001"
            },
            {
                "name": "Fitness Tracker Smart",
                "description": "Water-resistant fitness tracker with heart rate monitor and sleep tracking",
                "price": 129.99,
                "stock_quantity": 120,
                "category": "Sports",
                "sku": "FIT-TRACK-001"
            }
        ]
        
        # Create products
        created_products = []
        for product_data in sample_products:
            product = Product(
                **product_data,
                owner_id=admin_user.id,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(product)
            created_products.append(product)
        
        db.commit()
        
        print(f"✅ Created {len(created_products)} sample products successfully!")
        print("   Categories: Electronics, Sports, Home & Kitchen")
        print("   Price range: $45.00 - $1,199.99")
        print("   Stock quantities: 15 - 200 units")
        
        return len(created_products)
        
    except Exception as e:
        print(f"❌ Error creating sample products: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

def main():
    """Main function to initialize the database."""
    print("🗄️  Initializing Product Management API Database...")
    print()
    
    try:
        # Create tables
        print("📋 Creating database tables...")
        create_tables()
        print("✅ Database tables created successfully!")
        print()
        
        # Create superuser
        print("👤 Creating superuser...")
        superuser = create_superuser()
        print()
        
        # Create test user
        print("👤 Creating test user...")
        test_user = create_sample_data()
        print()
        
        # Create sample products
        print("📦 Creating sample products...")
        product_count = create_sample_products()
        print()
        
        print("🎉 Database initialization completed!")
        print()
        print("📚 You can now:")
        print("   1. Start the API with: python run.py")
        print("   2. Access the API docs at: http://localhost:8000/api/v1/docs")
        print("   3. Login with the created users")
        print("   4. Test product endpoints with sample data")
        print()
        print("🔐 Default credentials:")
        if superuser:
            print(f"   Superuser: {superuser.username} / AdminPass123")
        if test_user:
            print(f"   Test User: {test_user.username} / UserPass123")
        print()
        print("📦 Sample data:")
        print(f"   Products: {product_count} items across 3 categories")
        print("   Categories: Electronics, Sports, Home & Kitchen")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 