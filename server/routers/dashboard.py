\
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from .. import models, schemas
from ..dependencies import auth_deps

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/metrics", response_model=schemas.DashboardMetrics)
async def get_dashboard_metrics(
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.admin_required) # Metrics for admins
):
    logger.info(f"Admin {current_user.email} (store {current_user.store_id}) requesting dashboard metrics.")
    
    store_id = current_user.store_id

    try:
        # Total products in the admin's store
        total_products = db.query(func.count(models.Product.id)).filter(models.Product.store_id == store_id).scalar() or 0

        # Total items sold in the admin's store
        total_sold_items = db.query(func.sum(models.Sale.quantity)).filter(models.Sale.store_id == store_id).scalar() or 0
        
        # Total sales value in the admin's store
        # This assumes sales occur at product.max_sell_price
        # Sum of (sale.quantity * product.max_sell_price) for each sale
        query_total_sales_value = (
            db.query(func.sum(models.Sale.quantity * models.Product.max_sell_price))
            .join(models.Product, models.Sale.product_id == models.Product.id)
            .filter(models.Sale.store_id == store_id)
        )
        total_sales_value = query_total_sales_value.scalar() or 0.0

        logger.info(f"Metrics for store {store_id}: Products={total_products}, SalesValue={total_sales_value}, SoldItems={total_sold_items}")

        return schemas.DashboardMetrics(
            total_products=total_products,
            total_sales_value=round(total_sales_value, 2),
            total_sold_items=total_sold_items
        )
    except Exception as e:
        logger.error(f"Error calculating dashboard metrics for store {store_id}: {e}", exc_info=True)
        # Re-raise to let FastAPI handle it as a 500 Internal Server Error
        raise
