from sqlalchemy import Column, Integer, String, Float, Date
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    purchase_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    sell_price = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    net_profit = Column(Float, nullable=False)
