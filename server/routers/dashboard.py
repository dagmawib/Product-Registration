\
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
import logging

from .. import models, schemas # Assuming schemas.py will have DashboardMetrics
from ..dependencies import auth_deps

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/metrics", response_model=schemas.DashboardMetrics) # Define DashboardMetrics in schemas.py
async def get_dashboard_metrics(
    db: Session = Depends(auth_deps.get_db),
    current_user: models.User = Depends(auth_deps.admin_required) # Metrics usually for admins
) -> Dict[str, Any]:
    logger.info(f"Admin {current_user.email} requesting dashboard metrics.")
    try:
        total_products = db.query(func.count(models.Product.id)).scalar()
        total_sales_volume = db.query(func.sum(models.SoldProduct.sale_price * models.SoldProduct.quantity_sold)).scalar() or 0
        total_units_sold = db.query(func.sum(models.SoldProduct.quantity_sold)).scalar() or 0
        
        # Ensure User model has 'role' attribute for this query to work
        total_employees = db.query(func.count(models.User.id)).filter(models.User.role == 'employee').scalar()
        
        # Fallback for total_sales_volume and total_units_sold if they are None (e.g., no sales yet)
        total_sales_volume = total_sales_volume if total_sales_volume is not None else 0.0
        total_units_sold = total_units_sold if total_units_sold is not None else 0

        logger.info(f"Metrics calculated: Products={total_products}, SalesVol={total_sales_volume}, UnitsSold={total_units_sold}, Employees={total_employees}")

        return {
            "total_products": total_products,
            "total_sales_volume": round(total_sales_volume, 2),
            "total_units_sold": total_units_sold,
            "total_employees": total_employees
            # Add more metrics as needed, e.g., sales_by_store, top_selling_products
        }
    except Exception as e:
        logger.error(f"Error calculating dashboard metrics: {e}", exc_info=True)
        # Consider re-raising or returning a more specific error response
        # For now, returning zeros or error indicators might be an option,
        # but a 500 error from FastAPI due to an unhandled exception here is also possible.
        # Depending on requirements, you might want to return a 200 with error flags or default values.
        # For simplicity, if an error occurs, it will likely result in a 500 if not caught by FastAPI's error handling.
        # A more robust solution would catch specific database errors or calculation issues.
        # Re-raising to let FastAPI handle it as a 500 Internal Server Error:
        raise # This will make FastAPI return a 500 error if an exception occurs.
