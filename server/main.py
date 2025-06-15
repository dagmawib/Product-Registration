from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from . import models, database # Assuming models and database are correctly set up
from .routers import auth, products, sales, dashboard # Import routers
from .core import config # Import config

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Consider restricting this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(sales.router, prefix="/sales", tags=["sales"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# Example of how to access config if needed here, though typically not.
# logger.info(f"SECRET_KEY from config: {config.SECRET_KEY}")

@app.get("/")
async def root():
    return {"message": "Welcome to the Product Registration API"}

# Ensure any remaining specific endpoint logic previously in main.py is moved to appropriate routers.
# For example, if there were any root-level endpoints or general utility endpoints not fitting elsewhere.
# Based on the refactoring, most logic should now reside in the 'routers' modules.
