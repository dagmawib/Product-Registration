from itertools import product
from fastapi import FastAPI, Depends, HTTPException, status, Request # Added Request
from sqlalchemy.orm import Session
from . import models, schemas, database
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
import logging
from passlib.context import CryptContext # Restored
from jose import JWTError, jwt # Restored
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # Restored
from fastapi import Body
from typing import Optional

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

# --- Authentication and Security Setup --- RESTORED
SECRET_KEY = "your-secret-key-please-change-me"  # IMPORTANT: Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # Token validity period

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# tokenUrl points to the admin login endpoint, as employees will have a different login flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login_admin")

# --- Utility functions for password hashing and JWT --- RESTORED
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    from datetime import datetime, timedelta
    to_encode = data.copy()
    # Add expiry to the token
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Dependency to get current user --- RESTORED
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.SessionLocal)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: str = payload.get("sub") # 'sub' can be email for admin, or store:firstname:lastname for employee
        role: str = payload.get("role")
        if sub is None or role is None:
            logger.warning(f"Token missing sub or role. Payload: {payload}")
            raise credentials_exception
        
        user = None
        if role == "admin":
            user = db.query(models.User).filter(models.User.email == sub, models.User.role == "admin").first()
        elif role == "employee":
            # Employee 'sub' might be more complex, e.g., "storename:firstname:lastname"
            # This part needs to align with how employee tokens are created upon login
            # For now, assuming sub for employee is unique enough (e.g. user_id as string, or a composite key)
            # Let's assume for now employee login sets sub to user.id for simplicity in token, 
            # or a unique identifier that can be queried.
            # If sub is composite, parse it here.
            # For this restoration, let's assume sub for employee is their ID (requires employee login to set it this way)
            try:
                user_id = int(sub)
                user = db.query(models.User).filter(models.User.id == user_id, models.User.role == "employee").first()
            except ValueError:
                logger.error(f"Employee token 'sub' is not a valid ID: {sub}")
                raise credentials_exception
        
        if user is None:
            logger.warning(f"User not found for sub: {sub}, role: {role}")
            raise credentials_exception
        return user
    except JWTError as e:
        logger.error(f"JWTError decoding token: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}")
        raise credentials_exception

# --- Role-specific dependencies --- RESTORED
def admin_required(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required.")
    return current_user

def employee_required(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "employee":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Employee privileges required.")
    return current_user

# --- Database session dependency ---
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/sales", response_model=schemas.SaleOut, status_code=201)
def record_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(employee_required)):
    product = db.query(models.Product).filter(models.Product.id == sale.product_id, models.Product.store_id == current_user.store_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product not found or not in your store (Store ID: {current_user.store_id}).")
    if sale.quantity > product.quantity:
        raise HTTPException(status_code=400, detail="Not enough product quantity available.")
    # Reduce product quantity
    product.quantity -= sale.quantity
    # Calculate net profit for this sale
    net_profit = (product.sell_price - product.purchase_price) * sale.quantity
    product.net_profit += net_profit
    db_sale = models.Sale(
        product_id=sale.product_id,
        user_id=current_user.id, # Set from authenticated user
        store_id=current_user.store_id, # Set from authenticated user
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
        store_id=db_sale.store_id, # Ensure store_id is returned
        quantity=db_sale.quantity,
        timestamp=db_sale.timestamp
    )

@app.get("/sales", response_model=list[schemas.SaleOut])
def get_sales(db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    # Admins can view all sales for their store
    sales = db.query(models.Sale).filter(models.Sale.store_id == current_user.store_id).all()
    return [
        schemas.SaleOut(
            id=s.id,
            product_id=s.product_id,
            user_id=s.user_id,
            store_id=s.store_id,
            quantity=s.quantity,
            timestamp=s.timestamp
        ) for s in sales
    ]

@app.get("/dashboard/metrics")
def admin_dashboard_metrics(db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    # Metrics are for the admin's current store
    store_id = current_user.store_id
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
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    try:
        # Product store_id should match the admin's store_id
        if product.store_id != current_user.store_id:
            raise HTTPException(status_code=403, detail=f"Cannot create product for a different store (your store: {current_user.store_id}, requested: {product.store_id}).")
        
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
def get_products(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Any authenticated user (admin or employee) can get products for their store
    products = db.query(models.Product).filter(models.Product.store_id == current_user.store_id).all()
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
def update_product_put(product_id: int, product_update: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id, models.Product.store_id == current_user.store_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found or not in your store")

    # Ensure the product_update payload targets the same store_id
    if product_update.store_id != current_user.store_id:
        raise HTTPException(status_code=403, detail=f"Cannot change product's store to {product_update.store_id}. It must remain in your store ({current_user.store_id}).")

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
def update_product_patch(product_id: int, product_update: schemas.ProductUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id, models.Product.store_id == current_user.store_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found or not in your store")

    update_data = product_update.dict(exclude_unset=True)
    
    # Prevent changing store_id via PATCH
    if "store_id" in update_data and update_data["store_id"] != db_product.store_id:
        raise HTTPException(status_code=403, detail="Cannot change product's store_id via PATCH.")

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
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    # Admin can only delete products from their own store
    db_product = db.query(models.Product).filter(models.Product.id == product_id, models.Product.store_id == current_user.store_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found or not in your store")
    db.delete(db_product)
    db.commit()
    return None

# --- Authentication Endpoints --- RESTORED
@app.post("/auth/register_admin", response_model=schemas.AdminOut)
def register_admin(store_data: schemas.StoreCreate, db: Session = Depends(get_db)):
    existing_store = db.query(models.Store).filter(models.Store.name == store_data.storename).first()
    if existing_store:
        raise HTTPException(status_code=400, detail="Store name already exists.")
    
    existing_admin_email = db.query(models.User).filter(models.User.email == store_data.email, models.User.role == "admin").first()
    if existing_admin_email:
        raise HTTPException(status_code=400, detail="Admin email already registered.")

    db_store = models.Store(name=store_data.storename)
    db.add(db_store)
    db.commit()
    db.refresh(db_store)

    hashed_password = get_password_hash(store_data.password)
    admin_user = models.User(
        email=store_data.email, 
        phone_number=store_data.phone_number, 
        password_hash=hashed_password,
        role="admin",
        store_id=db_store.id
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return schemas.AdminOut(
        id=admin_user.id,
        email=admin_user.email,
        phone_number=admin_user.phone_number,
        storename=db_store.name,
        role=admin_user.role,
        store_id=admin_user.store_id
    )

@app.post("/auth/login_admin") # No response_model for token response by default
def login_admin(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username, models.User.role == "admin").first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "store_id": user.store_id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login_employee") # No response_model for token response by default
def login_employee(login_data: schemas.EmployeeLoginRequest, db: Session = Depends(get_db)):
    # Find the store first
    store = db.query(models.Store).filter(models.Store.name == login_data.storename).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid store name or employee credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Find the employee within that store
    user = db.query(models.User).filter(
        models.User.store_id == store.id,
        models.User.first_name == login_data.first_name,
        models.User.last_name == login_data.last_name,
        models.User.role == "employee"
    ).first()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid store name or employee credentials", # Keep generic for security
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create token with user ID as sub, role, and store_id
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role, "store_id": user.store_id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/add_employee", response_model=schemas.EmployeeOut)
def add_employee(employee_data: schemas.EmployeeCreate, db: Session = Depends(get_db), current_admin: models.User = Depends(admin_required)):
    # Admin can add employees to their own store.
    # employee_data.store_id is not needed in request as it comes from current_admin.store_id
    
    # Check if an employee with the same details (e.g., name) already exists in this store - optional
    # For simplicity, this check is omitted here but recommended in a real app.

    hashed_password = get_password_hash(employee_data.password)
    emp = models.User(
        first_name=employee_data.first_name,
        last_name=employee_data.last_name,
        phone_number=employee_data.phone_number,
        password_hash=hashed_password,
        role="employee",
        store_id=current_admin.store_id # Employee belongs to the admin's store
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
    return {"message": "Product Registration API is running (Auth Restored)."}
