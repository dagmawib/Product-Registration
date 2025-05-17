from .database import Base, engine
from .models import Product

# Create all tables
Base.metadata.create_all(bind=engine)
