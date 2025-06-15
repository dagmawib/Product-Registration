from .database import Base, engine
from .models import Product, User, Store  # Import User and Store models

# Drop all tables first to ensure schema updates
Base.metadata.drop_all(bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)
