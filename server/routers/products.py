\
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, models
from ..dependencies import auth_deps # Assuming get_db, admin_required, get_current_user are here


router = APIRouter()

# Add Product
@router.post("/", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: schemas.ProductCreate, # Input schema
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.admin_required)
):
    if product.store_id != current_user.store_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot create product for a different store (your store: {current_user.store_id}, requested: {product.store_id})."
        )

    # Calculate net_profit to be stored
    calculated_net_profit = (product.max_sell_price - product.purchase_price) * product.quantity

    db_product_data = product.model_dump()
    db_product = models.Product(**db_product_data, net_profit=calculated_net_profit)
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Calculate min_sell_price for the response
    min_sell_price = db_product.purchase_price * 1.20 # Assuming 20% markup for min_sell_price

    return schemas.ProductOut(
        id=db_product.id,
        name=db_product.name,
        category=db_product.category,
        purchase_price=db_product.purchase_price,
        quantity=db_product.quantity,
        max_sell_price=db_product.max_sell_price,
        date=db_product.date,
        store_id=db_product.store_id,
        net_profit=db_product.net_profit, # This is the stored net_profit
        min_sell_price=min_sell_price
    )

# Get All Products
@router.get("/", response_model=List[schemas.ProductOut])
async def read_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.get_current_user) # Any authenticated user
):
    products_query = db.query(models.Product).filter(models.Product.store_id == current_user.store_id)
    products = products_query.offset(skip).limit(limit).all()
    
    result = []
    for p in products:
        min_sell_price = p.purchase_price * 1.20
        result.append(schemas.ProductOut(
            id=p.id,
            name=p.name,
            category=p.category,
            purchase_price=p.purchase_price,
            quantity=p.quantity,
            max_sell_price=p.max_sell_price,
            date=p.date,
            store_id=p.store_id,
            net_profit=p.net_profit, # Use stored net_profit
            min_sell_price=min_sell_price
        ))
    return result

# Get Specific Product
@router.get("/{product_id}", response_model=schemas.ProductOut)
async def read_product(
    product_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.get_current_user) # Any authenticated user
):
    db_product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.store_id == current_user.store_id
    ).first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or not in your store")

    min_sell_price = db_product.purchase_price * 1.20
    return schemas.ProductOut(
        id=db_product.id,
        name=db_product.name,
        category=db_product.category,
        purchase_price=db_product.purchase_price,
        quantity=db_product.quantity,
        max_sell_price=db_product.max_sell_price,
        date=db_product.date,
        store_id=db_product.store_id,
        net_profit=db_product.net_profit, # Use stored net_profit
        min_sell_price=min_sell_price
    )

# Update Product (PUT - Full Update)
@router.put("/{product_id}", response_model=schemas.ProductOut)
async def update_product_put(
    product_id: int,
    product_update: schemas.ProductCreate, # Using ProductCreate for PUT as per snippet
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.admin_required)
):
    db_product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.store_id == current_user.store_id
    ).first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or not in your store")

    if product_update.store_id != current_user.store_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot change product's store to {product_update.store_id}. It must remain in your store ({current_user.store_id})."
        )

    update_data = product_update.model_dump()
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    # Recalculate and update net_profit
    db_product.net_profit = (db_product.max_sell_price - db_product.purchase_price) * db_product.quantity
    
    db.commit()
    db.refresh(db_product)

    min_sell_price = db_product.purchase_price * 1.20
    return schemas.ProductOut(
        id=db_product.id,
        name=db_product.name,
        category=db_product.category,
        purchase_price=db_product.purchase_price,
        quantity=db_product.quantity,
        max_sell_price=db_product.max_sell_price,
        date=db_product.date,
        store_id=db_product.store_id,
        net_profit=db_product.net_profit,
        min_sell_price=min_sell_price
    )

# Update Product (PATCH - Partial Update)
@router.patch("/{product_id}", response_model=schemas.ProductOut)
async def update_product_patch(
    product_id: int,
    product_update: schemas.ProductUpdate, # Using ProductUpdate for PATCH
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.admin_required)
):
    db_product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.store_id == current_user.store_id
    ).first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or not in your store")

    update_data = product_update.model_dump(exclude_unset=True)

    if "store_id" in update_data and update_data["store_id"] != db_product.store_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot change product's store_id via PATCH.")

    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    # Recalculate net_profit if relevant fields changed
    if any(key in update_data for key in ["max_sell_price", "purchase_price", "quantity"]):
        db_product.net_profit = (db_product.max_sell_price - db_product.purchase_price) * db_product.quantity
        
    db.commit()
    db.refresh(db_product)

    min_sell_price = db_product.purchase_price * 1.20
    return schemas.ProductOut(
        id=db_product.id,
        name=db_product.name,
        category=db_product.category,
        purchase_price=db_product.purchase_price,
        quantity=db_product.quantity,
        max_sell_price=db_product.max_sell_price,
        date=db_product.date,
        store_id=db_product.store_id,
        net_profit=db_product.net_profit,
        min_sell_price=min_sell_price
    )

# Delete Product
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.admin_required)
):
    db_product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.store_id == current_user.store_id
    ).first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or not in your store")
    
    db.delete(db_product)
    db.commit()
    return None
