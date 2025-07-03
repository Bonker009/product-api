"""
Advanced search functionality for products.
Supports multiple search methods: vector search, fuzzy search, full-text search, and filtering.
"""

import re
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models import Product

# Simple full-text search function

def full_text_search(db: Session, query: str, limit: int = 100):
    if not query:
        return []
    query_clean = re.sub(r'\s+', ' ', query.lower().strip())
    tokens = query_clean.split()
    if not tokens:
        return []
    search_conditions = []
    for token in tokens:
        if len(token) >= 2:
            token_condition = or_(
                Product.name.ilike(f"%{token}%"),
                Product.description.ilike(f"%{token}%"),
                Product.category.ilike(f"%{token}%"),
                Product.sku.ilike(f"%{token}%")
            )
            search_conditions.append(token_condition)
    if not search_conditions:
        return []
    combined_condition = or_(*search_conditions)
    results = db.query(Product).filter(
        and_(combined_condition, Product.is_active == True)
    ).limit(limit).all()
    return results 