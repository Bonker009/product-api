#!/usr/bin/env python3
"""
Simple test script to demonstrate the Product Management API functionality.
This script tests the main endpoints and shows how to use the API.
"""

import requests
import json
import time
from typing import Dict, Any

# API Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test data
TEST_USER = {
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePass123",
    "full_name": "Test User"
}

TEST_PRODUCT = {
    "name": "Test Product",
    "description": "A test product for demonstration",
    "price": 29.99,
    "stock_quantity": 100,
    "category": "Electronics",
    "sku": "TEST-001"
}

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.product_id = None
    
    def print_response(self, response: requests.Response, title: str):
        """Print formatted response."""
        print(f"\n{'='*50}")
        print(f"{title}")
        print(f"{'='*50}")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response: {response.text}")
        print(f"{'='*50}\n")
    
    def test_health_check(self):
        """Test health check endpoint."""
        print("Testing Health Check...")
        response = self.session.get(f"{BASE_URL}/health")
        self.print_response(response, "Health Check")
        return response.status_code == 200
    
    def test_register(self):
        """Test user registration."""
        print("Testing User Registration...")
        response = self.session.post(
            f"{API_BASE}/auth/register",
            json=TEST_USER
        )
        self.print_response(response, "User Registration")
        
        if response.status_code == 201:
            data = response.json()
            self.user_id = data.get("id")
            return True
        return False
    
    def test_login(self):
        """Test user login."""
        print("Testing User Login...")
        response = self.session.post(
            f"{API_BASE}/auth/login",
            data={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
        )
        self.print_response(response, "User Login")
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            return True
        return False
    
    def test_get_current_user(self):
        """Test getting current user info."""
        print("Testing Get Current User...")
        response = self.session.get(f"{API_BASE}/auth/me")
        self.print_response(response, "Get Current User")
        return response.status_code == 200
    
    def test_create_product(self):
        """Test product creation."""
        print("Testing Product Creation...")
        response = self.session.post(
            f"{API_BASE}/products/",
            json=TEST_PRODUCT
        )
        self.print_response(response, "Product Creation")
        
        if response.status_code == 201:
            data = response.json()
            self.product_id = data.get("id")
            return True
        return False
    
    def test_get_products(self):
        """Test getting products list."""
        print("Testing Get Products...")
        response = self.session.get(f"{API_BASE}/products/")
        self.print_response(response, "Get Products")
        return response.status_code == 200
    
    def test_get_product(self):
        """Test getting specific product."""
        if not self.product_id:
            print("No product ID available")
            return False
        
        print("Testing Get Specific Product...")
        response = self.session.get(f"{API_BASE}/products/{self.product_id}")
        self.print_response(response, "Get Specific Product")
        return response.status_code == 200
    
    def test_update_product(self):
        """Test product update."""
        if not self.product_id:
            print("No product ID available")
            return False
        
        print("Testing Product Update...")
        update_data = {
            "price": 39.99,
            "stock_quantity": 150,
            "description": "Updated test product description"
        }
        response = self.session.put(
            f"{API_BASE}/products/{self.product_id}",
            json=update_data
        )
        self.print_response(response, "Product Update")
        return response.status_code == 200
    
    def test_get_my_products(self):
        """Test getting user's products."""
        print("Testing Get My Products...")
        response = self.session.get(f"{API_BASE}/products/my-products")
        self.print_response(response, "Get My Products")
        return response.status_code == 200
    
    def test_get_statistics(self):
        """Test getting product statistics."""
        print("Testing Get Statistics...")
        response = self.session.get(f"{API_BASE}/products/statistics/overview")
        self.print_response(response, "Get Statistics")
        return response.status_code == 200
    
    def test_get_categories(self):
        """Test getting categories list."""
        print("Testing Get Categories...")
        response = self.session.get(f"{API_BASE}/products/categories/list")
        self.print_response(response, "Get Categories")
        return response.status_code == 200
    
    def test_product_filtering(self):
        """Test product filtering."""
        print("Testing Product Filtering...")
        params = {
            "category": "Electronics",
            "min_price": 10,
            "max_price": 50,
            "search": "test"
        }
        response = self.session.get(f"{API_BASE}/products/", params=params)
        self.print_response(response, "Product Filtering")
        return response.status_code == 200
    
    def test_delete_product(self):
        """Test product deletion."""
        if not self.product_id:
            print("No product ID available")
            return False
        
        print("Testing Product Deletion...")
        response = self.session.delete(f"{API_BASE}/products/{self.product_id}")
        self.print_response(response, "Product Deletion")
        return response.status_code == 200
    
    def test_validation_errors(self):
        """Test validation error handling."""
        print("Testing Validation Errors...")
        
        # Test invalid email
        invalid_user = TEST_USER.copy()
        invalid_user["email"] = "invalid-email"
        response = self.session.post(f"{API_BASE}/auth/register", json=invalid_user)
        self.print_response(response, "Invalid Email Validation")
        
        # Test invalid product
        invalid_product = TEST_PRODUCT.copy()
        invalid_product["price"] = -10  # Negative price
        response = self.session.post(f"{API_BASE}/products/", json=invalid_product)
        self.print_response(response, "Invalid Product Validation")
    
    def run_all_tests(self):
        """Run all tests in sequence."""
        print("Starting API Tests...")
        print(f"Base URL: {BASE_URL}")
        print(f"API Base: {API_BASE}")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_register),
            ("User Login", self.test_login),
            ("Get Current User", self.test_get_current_user),
            ("Create Product", self.test_create_product),
            ("Get Products", self.test_get_products),
            ("Get Specific Product", self.test_get_product),
            ("Update Product", self.test_update_product),
            ("Get My Products", self.test_get_my_products),
            ("Get Statistics", self.test_get_statistics),
            ("Get Categories", self.test_get_categories),
            ("Product Filtering", self.test_product_filtering),
            ("Delete Product", self.test_delete_product),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                print(f"\n{'*'*60}")
                print(f"Running: {test_name}")
                print(f"{'*'*60}")
                result = test_func()
                results.append((test_name, result))
                time.sleep(1)  # Small delay between tests
            except Exception as e:
                print(f"Error in {test_name}: {e}")
                results.append((test_name, False))
        
        # Test validation errors at the end
        try:
            self.test_validation_errors()
        except Exception as e:
            print(f"Error in validation tests: {e}")
        
        # Print summary
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        print(f"\nTotal: {passed}/{total} tests passed")


if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests() 