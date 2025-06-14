from itertools import product
from fastapi import FastAPI, Depends, HTTPException, status, Request # Added Request
from sqlalchemy.orm import Session
from . import models, schemas, database
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
import logging
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Body
from typing import Optional

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

# SECRET_KEY = "your-secret-key"  # Change this in production
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login_admin") # Not needed

# async def inspect_oauth_dependency(request: Request, token: str = Depends(oauth2_scheme)):
#     print(f"DEBUG [inspect_oauth_dependency]: Request query params: {request.query_params}")
#     print(f"DEBUG [inspect_oauth_dependency]: Token received: {'Yes' if token else 'No'}")
#     return token

#Utility functions for password hashing and JWT - no longer needed
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

# def create_access_token(data: dict):
#     from datetime import datetime, timedelta
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(days=30)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# def get_token_header(token: str = Depends(inspect_oauth_dependency)):
#     print(f"DEBUG [get_token_header]: Token successfully passed through inspect_oauth_dependency.")
#     return token

# def get_current_user(token: str = Depends(get_token_header)):
#     # This function is entirely removed as auth is gone.
#     # Endpoints will directly take IDs or rely on request body for context.
#     pass

# def admin_required(current_user: models.User = Depends(get_current_user)):
#     # This function is entirely removed.
#     pass

# def employee_required(current_user: models.User = Depends(get_current_user)):
#     # This function is entirely removed.
#     pass

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/sales", response_model=schemas.SaleOut, status_code=201)
# def record_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(employee_required)):
def record_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    # Assuming sale.store_id and sale.user_id (employee_id) are provided in the request body (schemas.SaleCreate)
    product = db.query(models.Product).filter(models.Product.id == sale.product_id, models.Product.store_id == sale.store_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product not found in store {sale.store_id}.")
    if sale.quantity > product.quantity:
        raise HTTPException(status_code=400, detail="Not enough product quantity available.")
    # Reduce product quantity
    product.quantity -= sale.quantity
    # Calculate net profit for this sale
    net_profit = (product.sell_price - product.purchase_price) * sale.quantity
    product.net_profit += net_profit
    db_sale = models.Sale(
        product_id=sale.product_id,
        user_id=sale.user_id, # Changed to sale.user_id
        quantity=sale.quantity,
        timestamp=sale.timestamp
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    # db.commit() # Second commit might be redundant here
    return schemas.SaleOut(
        id=db_sale.id,
        product_id=db_sale.product_id,
        user_id=db_sale.user_id,
        store_id=sale.store_id, # Ensure store_id is returned
        quantity=db_sale.quantity,
        timestamp=db_sale.timestamp
    )

@app.get("/sales", response_model=list[schemas.SaleOut])
# def get_sales(db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
def get_sales(store_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Sale).join(models.Product)
    if store_id:
        query = query.filter(models.Product.store_id == store_id)
    sales = query.all()
    return [
        schemas.SaleOut(
            id=s.id,
            product_id=s.product_id,
            user_id=s.user_id,
            store_id=s.product.store_id, # Get store_id from related product
            quantity=s.quantity,
            timestamp=s.timestamp
        ) for s in sales # Ensure product relationship is loaded or accessible
    ]

@app.get("/dashboard/metrics")
# def admin_dashboard_metrics(db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
def admin_dashboard_metrics(store_id: int, db: Session = Depends(get_db)): # store_id must be provided as a query parameter
    total_profit = db.query(models.Product).filter(models.Product.store_id == store_id).with_entities(db.func.sum(models.Product.net_profit)).scalar() or 0
    total_inventory = db.query(models.Product).filter(models.Product.store_id == store_id).with_entities(db.func.sum(models.Product.quantity)).scalar() or 0
    
    # Employee sales history - users making sales are employees
    # Query Sale object, and related employee's first_name and last_name
    sales_details = db.query(
        models.Sale, 
        models.User.first_name, 
        models.User.last_name
    ).join(
        models.User, models.Sale.user_id == models.User.id
    ).join(
        models.Product, models.Sale.product_id == models.Product.id
    ).filter(
        models.Product.store_id == store_id, # Filter by provided store_id
        models.User.role == "employee" 
    ).all()
    
    employee_sales = {}
    for sale, first_name, last_name in sales_details:
        employee_name = f"{first_name} {last_name}" if first_name and last_name else f"Employee ID: {sale.user_id}"
        if employee_name not in employee_sales:
            employee_sales[employee_name] = 0
        employee_sales[employee_name] += sale.quantity
        
    return {
        "total_profit": total_profit,
        "total_inventory": total_inventory,
        "employee_sales": employee_sales
    }

# Restrict product endpoints to admin only for create, update, delete - This restriction is now conceptual / based on API design
@app.post("/products", response_model=schemas.ProductOut, status_code=201)
# def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    # product.store_id must be provided in the request body (schemas.ProductCreate)
    try:
        # Ensure the store exists if creating a product for it
        store = db.query(models.Store).filter(models.Store.id == product.store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail=f"Store with id {product.store_id} not found.")

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
# def get_products(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
def get_products(store_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Product)
    if store_id:
        query = query.filter(models.Product.store_id == store_id)
    products = query.all()
    if not products:
        logger.info("No products found.")
        return []
    result = []
    for p in products:
        p.net_profit = (p.max_sell_price - p.purchase_price) * p.quantity
        min_sell_price = p.purchase_price * 1.2
        result.append(schemas.ProductOut(
            id=p.id,
            name=p.name,
            category=p.category,
            purchase_price=p.purchase_price,
            quantity=p.quantity,
            # sell_price=p.sell_price,
            max_sell_price=p.max_sell_price,
            date=p.date,
            store_id=p.store_id,  # Added store_id
            net_profit=p.net_profit,
            min_sell_price=min_sell_price
        ))
    logger.info(f"Fetched {len(result)} products.")
    return result

@app.put("/products/{product_id}", response_model=schemas.ProductOut)
# def update_product_put(product_id: int, product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
def update_product_put(product_id: int, product_update: schemas.ProductCreate, db: Session = Depends(get_db)):
    # product_update.store_id must be provided and should match the product's current store_id if not changing stores
    # or, if changing stores is allowed, ensure the new store_id exists.
    # For simplicity, let's assume store_id in product_update is the target store_id.
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Ensure the target store_id from the payload exists
    target_store_id = product_update.store_id
    store = db.query(models.Store).filter(models.Store.id == target_store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Target store with id {target_store_id} not found.")

    # Update all fields from the product schema
    for var, value in vars(product_update).items():
        setattr(db_product, var, value) 
    
    # db_product.store_id = target_store_id # Already set by loop if store_id is in ProductCreate

    db_product.net_profit = (db_product.max_sell_price - db_product.purchase_price) * db_product.quantity
    db.commit()
    db.refresh(db_product)
    
    response_data = {
        "id": db_product.id,
        "name": db_product.name,
        "category": db_product.category,
        "purchase_price": db_product.purchase_price,
        "quantity": db_product.quantity,
        # "sell_price": db_product.sell_price,
        "max_sell_price": db_product.max_sell_price,
        "date": db_product.date,
        "store_id": db_product.store_id,
        "net_profit": db_product.net_profit, # Assumes net_profit is a persisted column and correctly refreshed
        "min_sell_price": db_product.purchase_price * 1.2
    }
    return schemas.ProductOut(**response_data)

@app.patch("/products/{product_id}", response_model=schemas.ProductOut)
# def update_product_patch(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
def update_product_patch(product_id: int, product_update: schemas.ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_update.dict(exclude_unset=True)

    # If store_id is being updated, ensure the new store exists
    if "store_id" in update_data:
        new_store_id = update_data["store_id"]
        store = db.query(models.Store).filter(models.Store.id == new_store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail=f"Target store with id {new_store_id} not found for PATCH.")

    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    # Recalculate net_profit if relevant fields changed
    if any(key in update_data for key in ["purchase_price", "quantity"]):
        db_product.net_profit = (db_product.max_sell_price - db_product.purchase_price) * db_product.quantity

    db.commit()
    db.refresh(db_product)

    response_data = {
        "id": db_product.id,
        "name": db_product.name,
        "category": db_product.category,
        "purchase_price": db_product.purchase_price,
        "quantity": db_product.quantity,
        # "sell_price": db_product.sell_price,
        "max_sell_price": db_product.max_sell_price,
        "date": db_product.date,
        "store_id": db_product.store_id,
        "net_profit": db_product.net_profit, # Assumes net_profit is a persisted column and correctly refreshed
        "min_sell_price": db_product.purchase_price * 1.2
    }
    return schemas.ProductOut(**response_data)

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_product(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
def delete_product(product_id: int, store_id: int, db: Session = Depends(get_db)): # Require store_id for explicit deletion from a store
    db_product = db.query(models.Product).filter(models.Product.id == product_id, models.Product.store_id == store_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail=f"Product not found in store {store_id}")
    db.delete(db_product)
    db.commit()
    return None

# @app.post("/auth/register_admin", response_model=schemas.AdminOut)
# def register_admin(store: schemas.StoreCreate, db: Session = Depends(get_db)):
#     # This endpoint might be re-purposed to just create a store and a primary user for it.
#     # Or split into /stores and /users endpoints.
#     # For now, let's simplify it to create a store and an associated "admin" user without password.
#     existing_store = db.query(models.Store).filter(models.Store.name == store.storename).first()
#     if existing_store:
#         raise HTTPException(status_code=400, detail="Store name already exists.")
    
#     db_store = models.Store(name=store.storename)
#     db.add(db_store)
#     db.commit()
#     db.refresh(db_store)

#     # Create a user associated with this store
#     # Password is not hashed as it's removed from schema
#     admin_user = models.User(
#         email=store.email, 
#         phone_number=store.phone_number, 
#         # password_hash=get_password_hash(store.password), # No password
#         role="admin", # Or a default user role
#         store_id=db_store.id
#     )
#     db.add(admin_user)
#     db.commit()
#     db.refresh(admin_user)
#     return schemas.AdminOut(
#         id=admin_user.id,
#         email=admin_user.email,
#         phone_number=admin_user.phone_number,
#         storename=db_store.name,
#         role=admin_user.role,
#         store_id=admin_user.store_id
#     )

# Login endpoints are no longer needed
# @app.post(
#     "/auth/login_admin",
#     summary="Admin Login via Form",
#     description="Admin login using email and password. Expects `application/x-www-form-urlencoded` form data with a `username` field (for the admin's email) and a `password` field. This endpoint is used by Swagger's 'Authorize' button."
# )
# def login_admin(admin_credentials: schemas.AdminLogin, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.email == admin_credentials.email, models.User.role == "admin").first()
#     if not user or not verify_password(admin_credentials.password, user.password_hash):
#         raise HTTPException(status_code=400, detail="Incorrect email or password")
#     access_token = create_access_token(data={"sub": user.email, "role": user.role})
#     return {"access_token": access_token, "token_type": "bearer"}

# @app.post("/auth/login_employee")
# def login_employee(storename: str = Body(...), first_name: str = Body(...), last_name: str = Body(...), password: str = Body(...), db: Session = Depends(get_db)):
#     store = db.query(models.Store).filter(models.Store.name == storename).first()
#     if not store:
#         raise HTTPException(status_code=400, detail="Store not found")
#     user = db.query(models.User).filter(
#         models.User.store_id == store.id,
#         models.User.first_name == first_name,
#         models.User.last_name == last_name,
#         models.User.role == "employee"
#     ).first()
#     if not user or not verify_password(password, user.password_hash):
#         raise HTTPException(status_code=400, detail="Incorrect name or password")
#     access_token = create_access_token(data={"sub": f"{store.name}:{user.first_name}:{user.last_name}", "role": user.role})
#     return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users", response_model=schemas.EmployeeOut) # Renamed from /auth/add_employee
# def add_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
def create_user(employee_data: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    # employee_data.store_id must be provided in the request body (schemas.EmployeeCreate)
    # Ensure the store exists
    store = db.query(models.Store).filter(models.Store.id == employee_data.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail=f"Store with id {employee_data.store_id} not found.")

    # hashed_password = get_password_hash(employee.password) # No password
    emp = models.User(
        first_name=employee_data.first_name,
        last_name=employee_data.last_name,
        phone_number=employee_data.phone_number,
        # password_hash=hashed_password, # No password
        role="employee", # Or determine role based on request
        store_id=employee_data.store_id
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return schemas.EmployeeOut(
        id=emp.id,
        first_name=emp.first_name,
        last_name=emp.last_name,
        phone_number=emp.phone_number,
        role=emp.role,
        store_id=emp.store_id
    )

@app.get("/")
def root():
    return {"message": "Product Registration API is running (No Auth)."}
