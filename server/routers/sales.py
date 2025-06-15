\
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from .. import schemas, models
from ..dependencies import auth_deps
import logging # Added logging

logger = logging.getLogger(__name__) # Added logger

router = APIRouter()

# Register a Sale
@router.post("/", response_model=schemas.SaleOut, status_code=status.HTTP_201_CREATED) # Changed to SaleOut
async def create_sale( # Renamed function for clarity
    sale_data: schemas.SaleCreate, # Changed to SaleCreate and sale_data
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.employee_required) # Employee or Admin can register sales
):
    logger.info(f"User {current_user.id} attempting to register a sale for product {sale_data.product_id} in store {current_user.store_id}")
    # Check if product exists and belongs to the same store
    product = db.query(models.Product).filter(
        models.Product.id == sale_data.product_id,
        models.Product.store_id == current_user.store_id
    ).first()

    if not product:
        logger.warning(f"Product with id {sale_data.product_id} not found in store {current_user.store_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {sale_data.product_id} not found in your store.")

    # Check if product has enough quantity
    if product.quantity < sale_data.quantity:
        logger.warning(f"Not enough stock for product {product.id}. Available: {product.quantity}, Requested: {sale_data.quantity}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock.")

    db_sale = models.Sale( # Changed to models.Sale
        product_id=sale_data.product_id,
        quantity=sale_data.quantity,
        timestamp=sale_data.timestamp, # Ensure SaleCreate includes timestamp
        user_id=current_user.id,
        store_id=current_user.store_id
    )
    db.add(db_sale)
    
    # Update product quantity
    product.quantity -= sale_data.quantity
    
    db.commit()
    db.refresh(db_sale)
    logger.info(f"Sale registered successfully with ID: {db_sale.id}")
    return db_sale

# Get All Sales for the current user's store
@router.get("/", response_model=List[schemas.SaleOut]) # Changed to SaleOut
async def read_sales( # Renamed function for clarity
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.employee_required) # Or any authenticated user in the store
):
    logger.info(f"User {current_user.id} fetching sales for store {current_user.store_id}")
    sales = db.query(models.Sale).filter(models.Sale.store_id == current_user.store_id).offset(skip).limit(limit).all() # Changed to models.Sale and filtered by store_id
    logger.info(f"Retrieved {len(sales)} sales records for store {current_user.store_id}")
    return sales

# Get a specific sale by ID from the current user's store
@router.get("/{sale_id}", response_model=schemas.SaleOut) # Changed to SaleOut
async def read_sale( # Renamed function for clarity
    sale_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.employee_required) # Or any authenticated user
):
    logger.info(f"User {current_user.id} attempting to fetch sale {sale_id} from store {current_user.store_id}")
    sale = db.query(models.Sale).filter( # Changed to models.Sale
        models.Sale.id == sale_id,
        models.Sale.store_id == current_user.store_id # Ensure sale belongs to user's store
    ).first()
    if sale is None:
        logger.warning(f"Sale with id {sale_id} not found in store {current_user.store_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found in your store")
    logger.info(f"Successfully fetched sale {sale_id}")
    return sale

# Note: Updating or Deleting sales might be complex depending on business logic (e.g., returns, stock adjustments)
# For now, let's assume sales are immutable once created, or that specific processes handle returns/cancellations.

# Example: Delete a sale (Admin only, potentially for corrections)
@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sale(
    sale_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_admin: models.User = Depends(auth_deps.admin_required) # Only admin can delete
):
    logger.info(f"Admin {current_admin.email} (store {current_admin.store_id}) attempting to delete sale: {sale_id}")
    sale_to_delete = db.query(models.Sale).filter( # Changed to models.Sale
        models.Sale.id == sale_id,
        models.Sale.store_id == current_admin.store_id # Admin can only delete from their store
    ).first()

    if not sale_to_delete:
        logger.warning(f"Sale with id {sale_id} not found in store {current_admin.store_id} for deletion.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found in this store")

    # Important: Consider implications of deleting a sale.
    # Does this adjust product stock back? Are there audit trails?
    # For this example, we'll just delete the record.
    # And adjust product quantity back
    product = db.query(models.Product).filter(models.Product.id == sale_to_delete.product_id).first()
    if product:
        product.quantity += sale_to_delete.quantity
        logger.info(f"Adjusted stock for product {product.id} by +{sale_to_delete.quantity}")


    db.delete(sale_to_delete)
    db.commit()
    logger.info(f"Successfully deleted sale: {sale_id} from store {current_admin.store_id}")
    return None
