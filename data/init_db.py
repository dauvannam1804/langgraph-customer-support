import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Product, Order

# Get the directory of the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'ecommerce.db')
PRODUCTS_FILE_PATH = os.path.join(BASE_DIR, 'products.json')

# Create a database engine
engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)

def create_database_and_tables():
    """Creates the database and tables based on the defined models."""
    Base.metadata.create_all(engine)
    print("Database and tables created successfully.")

def populate_data():
    """Populates the database with product data from a JSON file."""
    Session = sessionmaker(bind=engine)
    session = Session()

    # Check if the database is already populated
    if session.query(Product).count() > 0:
        print("Database is already populated. Skipping data insertion.")
        return

    # Load product data from JSON file
    with open(PRODUCTS_FILE_PATH, 'r') as f:
        data = json.load(f)

    # Insert data into the database
    for category_data in data:
        category_name = category_data['category']
        for product_data in category_data['products']:
            product = Product(
                name=product_data['name'],
                category=category_name,
                price=product_data['price'],
                description=product_data['description']
            )
            session.add(product)

    # Commit the changes
    session.commit()
    print(f"✅ Database ecommerce.db has been populated with {session.query(Product).count()} sample products!")

if __name__ == "__main__":
    create_database_and_tables()
    populate_data()