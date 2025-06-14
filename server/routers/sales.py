\
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from .. import schemas, models
from ..dependencies import auth_deps

router = APIRouter()

# Add Sold Product (Register a Sale)
@router.post("/", response_model=schemas.SoldProductResponse, status_code=status.HTTP_201_CREATED)
async def create_sold_product(
    sold_product: schemas.SoldProductCreate,
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.employee_required) # Employee or Admin can register sales
):
    # Check if product exists
    product_exists = db.query(models.Product).filter(models.Product.id == sold_product.product_id).first()
    if not product_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {sold_product.product_id} not found.")

    # Check if product has enough stock (if you implement stock tracking)
    # if product_exists.stock < sold_product.quantity_sold:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock.")

    db_sold_product = models.SoldProduct(
        **sold_product.model_dump(),
        sold_by_user_id=current_user.id,
        date_sold=sold_product.date_sold if sold_product.date_sold else date.today() # Default to today if not provided
    )
    db.add(db_sold_product)
    
    # Update product stock (if you implement stock tracking)
    # product_exists.stock -= sold_product.quantity_sold
    
    db.commit()
    db.refresh(db_sold_product)
    return db_sold_product

# Get All Sold Products
@router.get("/", response_model=List[schemas.SoldProductResponse])
async def read_sold_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.employee_required) # Or any authenticated user
):
    sold_products = db.query(models.SoldProduct).offset(skip).limit(limit).all()
    return sold_products

# Get Specific Sold Product Record
@router.get("/{sold_product_id}", response_model=schemas.SoldProductResponse)
async def read_sold_product(
    sold_product_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.employee_required)
):
    db_sold_product = db.query(models.SoldProduct).filter(models.SoldProduct.id == sold_product_id).first()
    if db_sold_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sold product record not found")
    return db_sold_product

# Update Sold Product Record (e.g., correct a typo, not for changing fundamental sale data)
@router.put("/{sold_product_id}", response_model=schemas.SoldProductResponse)
async def update_sold_product(
    sold_product_id: int,
    sold_product_update: schemas.SoldProductUpdate, # Schema for what can be updated
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.admin_required) # Typically admin for corrections
):
    db_sold_product = db.query(models.SoldProduct).filter(models.SoldProduct.id == sold_product_id).first()
    if db_sold_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sold product record not found")

    update_data = sold_product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sold_product, key, value)
    
    # Potentially update 'last_modified_by_user_id' if you track that
    # db_sold_product.last_modified_by_user_id = current_user.id
    
    db.commit()
    db.refresh(db_sold_product)
    return db_sold_product

# Delete Sold Product Record (use with caution, typically admin only)
@router.delete("/{sold_product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sold_product(
    sold_product_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.admin_required)
):
    db_sold_product = db.query(models.SoldProduct).filter(models.SoldProduct.id == sold_product_id).first()
    if db_sold_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sold product record not found")
    
    # Consider implications: does deleting a sale revert stock? (if stock is tracked)
    # product = db.query(models.Product).filter(models.Product.id == db_sold_product.product_id).first()
    # if product:
    # product.stock += db_sold_product.quantity_sold

    db.delete(db_sold_product)
    db.commit()
    return None
