from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from data.models import Product, Order

# Kết nối tới SQLite
DATABASE_URL = "sqlite:///data/ecommerce.db"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
session = Session()


mcp = FastMCP(
    "sales_support",
    instructions = \
"""This server provides tools for a multi-agent sales system. \nIt helps with managing products, checking stock, creating orders, and providing customer support.

Available tools:
- search_products: Search for products based on keywords or categories.
- create_order: Creates a new order for a customer.
- check_order_status: Checks the status of an existing order.
"""
)

@mcp.tool()
def search_products(query: str) -> list:
    """Search for products in a specific category. The query must be one of 'Laptop', 'Smartphone', 'Tablet', 'Smartwatch', 'Accessory'."""
    print(f"[debug-server] search_products({query})")
    
    VALID_CATEGORIES = ["Laptop", "Smartphone", "Tablet", "Smartwatch", "Accessory"]
    
    if query not in VALID_CATEGORIES:
        return [f"Invalid category. Please use one of the following: {VALID_CATEGORIES}"]

    results = []
    products = session.query(Product).filter(Product.category == query).limit(10).all()

    for product in products:
        results.append({
            "product_id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description,
        })

    return results if results else ["No matching products found."]

@mcp.tool()
def create_order(user_name: str, address: str, product_id: int, amount: int) -> dict:
    """Creates a new order for a customer."""
    print(f"[debug-server] create_order({user_name}, {address}, {product_id}, {amount})")
    
    try:
        order = Order(
            user_name=user_name,
            address=address,
            product_id=product_id,
            amount=amount
        )
        session.add(order)
        session.commit()
        return {"order_id": order.id, "status": order.status}
    except Exception as e:
        session.rollback()
        return {"error": str(e)}

@mcp.tool()
def check_order_status(order_id: int) -> dict:
    """Checks the status of an existing order."""
    print(f"[debug-server] check_order_status({order_id})")
    
    try:
        order = session.query(Order).filter(Order.id == order_id).first()
        if order:
            return {"order_id": order.id, "status": order.status}
        else:
            return {"error": "Order not found."}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Initialize and run the server
    print("Starting MCP server...")
    mcp.run(transport="stdio") 