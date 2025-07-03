# Product Management API

A comprehensive FastAPI-based product management system with JWT authentication, comprehensive validation, robust error handling, and **advanced search capabilities**.

## Features

- 🔐 **JWT Authentication** - Secure token-based authentication
- 👥 **User Management** - User registration, login, and role-based access control
- 📦 **Product Management** - Full CRUD operations for products
- 🎯 **Smart Filtering** - Price, category, stock, and multi-criteria filtering
- 📊 **Statistics** - Product statistics and analytics
- ✅ **Comprehensive Validation** - Input validation using Pydantic
- 🛡️ **Security** - Password hashing, CORS protection, error handling
- 📄 **Pagination** - Efficient data pagination
- 📚 **API Documentation** - Auto-generated Swagger/OpenAPI docs
- 🤖 **Auto-Generated SKUs** - Automatic unique SKU generation

## Tech Stack

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type annotations
- **JWT** - JSON Web Tokens for authentication
- **bcrypt** - Password hashing
- **SQLite/PostgreSQL** - Database support
- **Sentence Transformers** - Vector search capabilities
- **FuzzyWuzzy** - Fuzzy string matching
- **jieba** - Chinese text tokenization

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd test-api-pilot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the environment example file and configure it:

```bash
cp env.example .env
```

Edit `.env` file with your configuration:

```env
# Database Configuration
DATABASE_URL=sqlite:///./product_management.db

# JWT Configuration
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
DEBUG=True
API_V1_STR=/api/v1
PROJECT_NAME=Product Management API

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Security Configuration
BCRYPT_ROUNDS=12
```

### 3. Initialize Database

```bash
# Initialize database and create default users
python init_db.py
```

### 4. Run the Application

```bash
# Run with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python run.py
```

### 5. Access the API

- **API Documentation**: http://localhost:8000/api/v1/docs
- **ReDoc Documentation**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login with form data |
| POST | `/api/v1/auth/login-alt` | Login with JSON |
| GET | `/api/v1/auth/me` | Get current user info |

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products/` | Get all products (with filtering) |
| POST | `/api/v1/products/` | Create new product |
| GET | `/api/v1/products/{id}` | Get specific product |
| PUT | `/api/v1/products/{id}` | Update product |
| DELETE | `/api/v1/products/{id}` | Delete product |
| GET | `/api/v1/products/my-products` | Get user's products |
| GET | `/api/v1/products/statistics/overview` | Get user statistics |
| GET | `/api/v1/products/categories/list` | Get all categories |

### Advanced Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products/search` | Advanced search with multiple methods |
| GET | `/api/v1/products/search/suggestions` | Get search suggestions |
| GET | `/api/v1/products/search/methods` | Get available search methods |

### Users (Admin Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/` | Get all users |
| GET | `/api/v1/users/{id}` | Get specific user |
| PUT | `/api/v1/users/{id}` | Update user |
| DELETE | `/api/v1/users/{id}` | Delete user |

## Advanced Search Features

### Search Methods

The API supports multiple search methods for different use cases:

#### 1. **Combined Search** (Default)
- Uses full-text search first, falls back to fuzzy search
- Best for general-purpose search
- Fast and accurate

#### 2. **Vector Search**
- Semantic vector search using sentence transformers
- Understands meaning, not just keywords
- Best for semantic similarity
- Requires `sentence-transformers` package

#### 3. **Fuzzy Search**
- Fuzzy string matching with similarity scoring
- Handles typos and misspellings
- Good for user input with errors

#### 4. **Full-text Search**
- Traditional SQL LIKE/ILIKE search
- Fast and exact matching
- Good for precise searches

### Search Examples

#### Basic Search
```bash
# Search for products containing "laptop"
curl -X GET "http://localhost:8000/api/v1/products/search?query=laptop" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Vector Search
```bash
# Semantic search for "computer" (will find laptops, desktops, etc.)
curl -X GET "http://localhost:8000/api/v1/products/search?query=computer&search_method=vector" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Fuzzy Search
```bash
# Search with typo tolerance
curl -X GET "http://localhost:8000/api/v1/products/search?query=cofee&search_method=fuzzy" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Advanced Filtering
```bash
# Search with multiple filters
curl -X GET "http://localhost:8000/api/v1/products/search?query=electronics&category=Electronics&min_price=100&max_price=1000&sort_by=price&sort_order=desc" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Search Suggestions
```bash
# Get autocomplete suggestions
curl -X GET "http://localhost:8000/api/v1/products/search/suggestions?query=lap" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search query |
| `search_method` | string | Search method (combined, vector, fuzzy, fulltext) |
| `category` | string | Filter by category |
| `min_price` | float | Minimum price filter |
| `max_price` | float | Maximum price filter |
| `min_stock` | int | Minimum stock filter |
| `max_stock` | int | Maximum stock filter |
| `sort_by` | string | Sort field (name, price, stock_quantity, created_at) |
| `sort_order` | string | Sort order (asc, desc) |
| `limit` | int | Number of results (max 1000) |
| `offset` | int | Number of results to skip |

## Usage Examples

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123",
    "full_name": "Test User"
  }'
```

### 2. Login and Get Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=SecurePass123"
```

### 3. Create a Product (Auto-Generated SKU)

```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sample Product",
    "description": "A sample product description",
    "price": 29.99,
    "stock_quantity": 100,
    "category": "Electronics"
  }'
```

### 4. Advanced Search with Filtering

```bash
curl -X GET "http://localhost:8000/api/v1/products/search?query=electronics&category=Electronics&min_price=10&max_price=500&sort_by=price&sort_order=asc" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Data Validation

The API includes comprehensive validation:

### User Registration
- **Email**: Must be valid email format
- **Username**: 3-100 characters, alphanumeric and underscore only
- **Password**: 8-100 characters, must contain uppercase, lowercase, and digit
- **Full Name**: Optional, max 200 characters

### Product Creation
- **Name**: 1-200 characters, required
- **Price**: Must be positive number
- **Stock Quantity**: Must be non-negative integer
- **SKU**: Optional, auto-generated if not provided
- **Category**: Optional, max 100 characters

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with configurable rounds
- **CORS Protection**: Configurable cross-origin requests
- **Input Validation**: Comprehensive Pydantic validation
- **Error Handling**: Structured error responses
- **Role-based Access**: User and superuser permissions

## Error Handling

The API provides structured error responses:

```json
{
  "error": true,
  "message": "Validation error",
  "details": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ],
  "status_code": 422
}
```

## Database

The application uses SQLAlchemy with support for:
- **SQLite** (default for development)
- **PostgreSQL** (production ready)

Database tables are automatically created on startup.

## Development

### Project Structure

```
test-api-pilot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication logic
│   ├── crud.py              # CRUD operations
│   ├── search.py            # Advanced search engine
│   └── api/
│       ├── __init__.py
│       ├── auth.py          # Auth endpoints
│       ├── products.py      # Product endpoints
│       └── users.py         # User endpoints
├── requirements.txt
├── env.example
├── init_db.py               # Database initialization
├── run.py                   # Application runner
├── test_api.py              # API tests
├── test_search.py           # Search tests
└── README.md
```

### Running Tests

```bash
# Test basic API functionality
python test_api.py

# Test advanced search functionality
python test_search.py
```

### Code Quality

```bash
# Install linting tools
pip install black isort flake8

# Format code
black app/
isort app/

# Lint code
flake8 app/
```

## Production Deployment

### Environment Variables

For production, ensure you have:

1. **Strong SECRET_KEY**: At least 32 characters
2. **Production Database**: PostgreSQL recommended
3. **Debug Mode**: Set to False
4. **CORS Origins**: Configure allowed origins

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository. 