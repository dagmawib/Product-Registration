from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    users = relationship("User", back_populates="store")
    products = relationship("Product", back_populates="store")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=True)  # Required for admins, optional for employees
    phone_number = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    name = Column(String, nullable=True)  # Display name for employees
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # User role: 'admin' or 'employee'
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    store = relationship("Store", back_populates="users")
    sales = relationship("Sale", back_populates="user")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    purchase_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    # sell_price = Column(Float, nullable=False)
    max_sell_price = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    net_profit = Column(Float, nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    store = relationship("Store", back_populates="products")
    sales = relationship("Sale", back_populates="product")

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    timestamp = Column(Date, nullable=False)
    product = relationship("Product", back_populates="sales")
    user = relationship("User", back_populates="sales")
