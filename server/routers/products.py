\
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, models
from ..dependencies import auth_deps

router = APIRouter()

# Add Product
@router.post("/", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.employee_required) # Or admin_required if only admins can add
):
    db_product = models.Product(**product.model_dump(), added_by_user_id=current_user.id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Get All Products
@router.get("/", response_model=List[schemas.ProductResponse])
async def read_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.employee_required) # Or any authenticated user
):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

# Get Specific Product
@router.get("/{product_id}", response_model=schemas.ProductResponse)
async def read_product(
    product_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.employee_required)
):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return db_product

# Update Product
@router.put("/{product_id}", response_model=schemas.ProductResponse)
async def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.employee_required) # Or admin_required
):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    # Potentially update 'updated_by_user_id' if you track that
    # db_product.updated_by_user_id = current_user.id 
    
    db.commit()
    db.refresh(db_product)
    return db_product

# Delete Product
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.admin_required) # Typically admin only
):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return None
