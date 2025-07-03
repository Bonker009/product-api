#!/usr/bin/env python3
"""
Test script to demonstrate the advanced search functionality.
"""

import requests
import json
import time

# API Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Sample products for testing
SAMPLE_PRODUCTS = [
    {
        "name": "Gaming Laptop Pro",
        "description": "High-performance gaming laptop with RTX 4080 graphics",
        "price": 2499.99,
        "stock_quantity": 25,
        "category": "Electronics"
    },
    {
        "name": "Wireless Bluetooth Headphones",
        "description": "Noise-cancelling wireless headphones with premium sound quality",
        "price": 199.99,
        "stock_quantity": 150,
        "category": "Electronics"
    },
    {
        "name": "Organic Coffee Beans",
        "description": "Premium organic coffee beans from Colombia, medium roast",
        "price": 24.99,
        "stock_quantity": 200,
        "category": "Food & Beverages"
    }
]


class SearchTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
    
    def login(self):
        """Login to get authentication token."""
        print("🔐 Logging in...")
        
        # Login
        login_data = {
            "username": "testuser",
            "password": "UserPass123"
        }
        
        response = self.session.post(f"{API_BASE}/auth/login-alt", json=login_data)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            print("✅ Login successful")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    
    def create_sample_products(self):
        """Create sample products for testing."""
        print("\n📦 Creating sample products...")
        
        for product_data in SAMPLE_PRODUCTS:
            try:
                response = self.session.post(f"{API_BASE}/products/", json=product_data)
                if response.status_code == 201:
                    product = response.json()
                    print(f"✅ Created: {product['name']} (SKU: {product['sku']})")
                else:
                    print(f"❌ Failed to create {product_data['name']}: {response.status_code}")
            except Exception as e:
                print(f"❌ Error creating {product_data['name']}: {e}")
    
    def test_search_methods(self):
        """Test different search methods."""
        print("\n🔍 Testing Search Methods...")
        
        # Test basic search
        print("\n1️⃣ Basic Search:")
        response = self.session.get(f"{API_BASE}/products/search?query=laptop")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {data['total']} products for 'laptop'")
            for product in data['items'][:3]:
                print(f"   - {product['name']} (${product['price']})")
        
        # Test fuzzy search
        print("\n2️⃣ Fuzzy Search:")
        response = self.session.get(f"{API_BASE}/products/search?query=cofee&search_method=fuzzy")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {data['total']} products for 'cofee' (fuzzy)")
            for product in data['items'][:3]:
                print(f"   - {product['name']} (${product['price']})")
        
        # Test filtering
        print("\n3️⃣ Filtering:")
        response = self.session.get(f"{API_BASE}/products/search?category=Electronics&min_price=100")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {data['total']} Electronics products over $100")
            for product in data['items'][:3]:
                print(f"   - {product['name']} (${product['price']})")
    
    def run_all_tests(self):
        """Run all search tests."""
        print("🚀 Starting Advanced Search Tests...")
        
        # Login
        if not self.login():
            print("❌ Cannot proceed without authentication")
            return
        
        # Create sample products
        self.create_sample_products()
        
        # Wait a moment
        time.sleep(2)
        
        # Test search methods
        self.test_search_methods()
        
        print("\n🎉 Search tests completed!")


if __name__ == "__main__":
    tester = SearchTester()
    tester.run_all_tests() 