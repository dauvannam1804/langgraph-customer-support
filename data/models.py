from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String)
    orders = relationship("Order", back_populates="product")

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String, default='pending')
    product = relationship("Product", back_populates="orders")
