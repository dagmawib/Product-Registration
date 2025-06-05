from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
import logging

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/products", response_model=schemas.ProductOut, status_code=201)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    try:
        db_product = models.Product(**product.dict(), net_profit=0)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info(f"Product created: {db_product.name}")
        # Calculate min_sell_price for response
        min_sell_price = db_product.purchase_price + (db_product.purchase_price * 0.2)
        return schemas.ProductOut(
            **product.dict(),
            id=db_product.id,
            net_profit=db_product.net_profit,
            min_sell_price=min_sell_price
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Failed to create product.")

@app.get("/products", response_model=list[schemas.ProductOut])
def get_products(db: Session = Depends(get_db)):
    try:
        products = db.query(models.Product).all()
        result = []
        for p in products:
            p.net_profit = (p.sell_price - p.purchase_price) * p.quantity
            min_sell_price = p.purchase_price * 1.2
            result.append(schemas.ProductOut(
                id=p.id,
                name=p.name,
                category=p.category,
                purchase_price=p.purchase_price,
                quantity=p.quantity,
                sell_price=p.sell_price,
                max_sell_price=p.max_sell_price,
                date=p.date,
                net_profit=p.net_profit,
                min_sell_price=min_sell_price
            ))
        logger.info(f"Fetched {len(result)} products.")
        return result
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch products.")
