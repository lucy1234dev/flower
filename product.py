"""
Product API for Flower Shop.

Handles adding, listing, and saving product data in JSON format.

Author: Your Name
Date: 2025-06-19
"""

import os
import uuid
import json
from typing import List, Dict, Any

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# Constants
DATA_DIR = "data"
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
os.makedirs(DATA_DIR, exist_ok=True)

def ensure_file_exists(file_path: str) -> None:
    """Create the file with [] if it doesn't exist (for products)."""
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f)


class ProductCreate(BaseModel):
    """Schema for creating a product."""
    name: str
    price: float
    categories: str
    page: str
    image: str


class Product(ProductCreate):
    """Schema for returning product with ID."""
    id: str
class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: str
    price: float
    categories: str
    page: str
    image: str


def load_products() -> List[Dict[str, Any]]:
    """
    Load products from the JSON file.

    Returns:
        List[Dict[str, Any]]: List of products.
    """
    ensure_file_exists(PRODUCTS_FILE)

    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_products(products: List[Dict[str, Any]]) -> None:
    """
    Save product list to JSON file.

    Args:
        products (List[Dict[str, Any]]): List of products to save.
    """
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as file:
        json.dump(products, file, indent=2)


@router.get("/products", response_model=List[Product])
def get_products():
    """
    Get all products.

    Returns:
        List[Product]: List of all products.
    """
    return load_products()


@router.post("/product", response_model=Product)
def add_product(product: ProductCreate):
    """
    Add a new product to the list.

    Args:
        product (ProductCreate): Product data.

    Returns:
        Product: The added product with ID.
    """

    products = load_products()

    new_product = {
        "id": str(uuid.uuid4()),
        "name": product.name,
        "price": product.price,
        "categories": product.categories,
        "page": product.page,
        "image": product.image
    }

    products.append(new_product)
    save_products(products)

    return new_product

from fastapi import HTTPException, Path

@router.delete("/delete-product/{product_id}")
def delete_product(product_id: str = Path(..., description="ID of the product to delete")):
    """
    Delete a product by its ID.

    Args:
        product_id (str): The ID of the product to delete.

    Returns:
        dict: Success message.
    """
    products = load_products()

    #  Look for the product by ID
    matching_product = next((p for p in products if p["id"] == product_id), None)

    #  If it’s not found, return error
    if not matching_product:
        raise HTTPException(status_code=404, detail="Product not found.")

    #  Remove it from the list
    updated_products = [p for p in products if p["id"] != product_id]

    #  Save the new product list
    save_products(updated_products)

    return {"message": f" Product with ID {product_id} deleted successfully."}
@router.put("/update-product/{product_id}", response_model=Product)
def update_product(product_id: str, updated: ProductUpdate):
    """
    Update an existing product.

    Args:
        product_id (str): The ID of the product to update.
        updated (ProductUpdate): New data for the product.

    Returns:
        Product: The updated product.
    """
    products = load_products()
    for product in products:
        if product["id"] == product_id:
            product["name"] = updated.name
            product["price"] = updated.price
            product["categories"] = updated.categories
            product["page"] = updated.page
            product["image"] = updated.image
            save_products(products)
            return product

    raise HTTPException(status_code=404, detail="Product not found.")


