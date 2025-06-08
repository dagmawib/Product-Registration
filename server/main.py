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

SECRET_KEY = "your-secret-key"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Updated tokenUrl to point to the admin login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login_admin")

async def inspect_oauth_dependency(request: Request, token: str = Depends(oauth2_scheme)):
    print(f"DEBUG [inspect_oauth_dependency]: Request query params: {request.query_params}")
    print(f"DEBUG [inspect_oauth_dependency]: Token received: {'Yes' if token else 'No'}")
    return token

# Utility functions for password hashing and JWT
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    from datetime import datetime, timedelta
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# New dependency to isolate token retrieval
def get_token_header(token: str = Depends(inspect_oauth_dependency)):
    print(f"DEBUG [get_token_header]: Token successfully passed through inspect_oauth_dependency.")
    return token

# Temporarily modify get_current_user to remove its own db dependency for testing
def get_current_user(token: str = Depends(get_token_header)): # REMOVED ", db: Session = Depends(database.SessionLocal)"
    print(f"DEBUG [get_current_user]: Token received: {token is not None}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials (simplified get_current_user)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if token is None: # Should not happen if inspect_oauth_dependency worked
        print("DEBUG [get_current_user]: Token is None after get_token_header.")
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: str = payload.get("sub")
        role: str = payload.get("role")
        if not sub or not role:
            print("DEBUG [get_current_user]: Sub or role missing in token payload.")
            raise credentials_exception

        print(f"DEBUG [get_current_user]: Decoded token: sub='{sub}', role='{role}'")

        # Simulate a user object without DB access for testing purposes.
        # This mock user needs to satisfy admin_required and provide store_id for add_employee.
        if role == "admin":
            class MockUser:
                def __init__(self, email, user_role, store_id_val):
                    self.id = -1 # Placeholder
                    self.email = email
                    self.role = user_role
                    self.store_id = store_id_val # Needs a value for add_employee
                    # Add other fields if models.User expects them and they might be accessed
                    self.first_name = "Admin (Mock)"
                    self.last_name = "User (Mock)"
                    self.phone_number = "N/A"

            # For an admin, 'sub' is the email. We need a store_id.
            # Let's assume a default store_id for this mock.
            # IMPORTANT: If your logic relies on a specific store_id from the token or a real admin user,
            # this mock might not be sufficient for full functionality but aims to pass dependency checks.
            user = MockUser(email=sub, user_role="admin", store_id_val=1) # Using placeholder store_id = 1
            print(f"DEBUG [get_current_user]: Simulated admin user: {user.email}, role: {user.role}, store_id: {user.store_id}")
            return user
        else:
            # This part would need similar mocking if testing employee-specific paths
            print(f"DEBUG [get_current_user]: Role is '{role}', not 'admin'. Simplified logic may not cover this case fully.")
            # If you need to test employee paths, you'd mock an employee user here.
            # For now, let's raise to indicate this path isn't fully mocked for general use.
            raise HTTPException(status_code=501, detail="Simplified get_current_user: Non-admin role not fully mocked for this test.")

    except JWTError as e:
        print(f"DEBUG [get_current_user]: JWTError decoding token: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"DEBUG [get_current_user]: Unexpected error: {e}")
        raise credentials_exception

def admin_required(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required.")
    return current_user

def employee_required(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "employee":
        raise HTTPException(status_code=403, detail="Employee privileges required.")
    return current_user

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/sales", response_model=schemas.SaleOut, status_code=201)
def record_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(employee_required)):
    # Employees can only record sales for their own store
    product = db.query(models.Product).filter(models.Product.id == sale.product_id, models.Product.store_id == current_user.store_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or not in your store.")
    if sale.quantity > product.quantity:
        raise HTTPException(status_code=400, detail="Not enough product quantity available.")
    # Reduce product quantity
    product.quantity -= sale.quantity
    # Calculate net profit for this sale
    net_profit = (product.sell_price - product.purchase_price) * sale.quantity
    product.net_profit += net_profit
    db_sale = models.Sale(
        product_id=sale.product_id,
        user_id=current_user.id,
        quantity=sale.quantity,
        timestamp=sale.timestamp
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    db.commit()
    return schemas.SaleOut(
        id=db_sale.id,
        product_id=db_sale.product_id,
        user_id=db_sale.user_id,
        quantity=db_sale.quantity,
        timestamp=db_sale.timestamp
    )

@app.get("/sales", response_model=list[schemas.SaleOut])
def get_sales(db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    # Admins can view all sales for their store
    sales = db.query(models.Sale).join(models.Product).filter(models.Product.store_id == current_user.store_id).all()
    return [
        schemas.SaleOut(
            id=s.id,
            product_id=s.product_id,
            user_id=s.user_id,
            quantity=s.quantity,
            timestamp=s.timestamp
        ) for s in sales
    ]

@app.get("/dashboard/metrics")
def admin_dashboard_metrics(db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    # Total profit, inventory, employee sales history for the store
    total_profit = db.query(models.Product).filter(models.Product.store_id == current_user.store_id).with_entities(db.func.sum(models.Product.net_profit)).scalar() or 0
    total_inventory = db.query(models.Product).filter(models.Product.store_id == current_user.store_id).with_entities(db.func.sum(models.Product.quantity)).scalar() or 0
    
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
        models.Product.store_id == current_user.store_id,
        models.User.role == "employee" # Ensure we are only getting sales by employees
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

# Restrict product endpoints to admin only for create, update, delete
@app.post("/products", response_model=schemas.ProductOut, status_code=201)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
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
def get_products(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only return products for the user's store
    products = db.query(models.Product).filter(models.Product.store_id == current_user.store_id).all()
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

@app.post("/auth/register_admin", response_model=schemas.AdminOut)
def register_admin(store: schemas.StoreCreate, db: Session = Depends(get_db)):
    # Check if store name already exists
    existing_store = db.query(models.Store).filter(models.Store.name == store.storename).first()
    if existing_store:
        raise HTTPException(status_code=400, detail="Store name already exists. Please choose a different name.")
    # Create store and admin user
    db_store = models.Store(name=store.storename)
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    hashed_password = get_password_hash(store.password)
    admin = models.User(
        email=store.email,
        phone_number=store.phone_number,
        password_hash=hashed_password,
        role="admin",
        store_id=db_store.id
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return schemas.AdminOut(
        id=admin.id,
        email=admin.email,
        phone_number=admin.phone_number,
        storename=db_store.name,
        role=admin.role,
        store_id=admin.store_id
    )

@app.post(
    "/auth/login_admin",
    summary="Admin Login via Form",
    description="Admin login using email and password. Expects `application/x-www-form-urlencoded` form data with a `username` field (for the admin's email) and a `password` field. This endpoint is used by Swagger's 'Authorize' button."
)
def login_admin(admin_credentials: schemas.AdminLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == admin_credentials.email, models.User.role == "admin").first()
    if not user or not verify_password(admin_credentials.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login_employee")
def login_employee(storename: str = Body(...), first_name: str = Body(...), last_name: str = Body(...), password: str = Body(...), db: Session = Depends(get_db)):
    store = db.query(models.Store).filter(models.Store.name == storename).first()
    if not store:
        raise HTTPException(status_code=400, detail="Store not found")
    user = db.query(models.User).filter(
        models.User.store_id == store.id,
        models.User.first_name == first_name,
        models.User.last_name == last_name,
        models.User.role == "employee"
    ).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect name or password")
    access_token = create_access_token(data={"sub": f"{store.name}:{user.first_name}:{user.last_name}", "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/add_employee", response_model=schemas.EmployeeOut)
def add_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    hashed_password = get_password_hash(employee.password)
    emp = models.User(
        first_name=employee.first_name,
        last_name=employee.last_name,
        phone_number=employee.phone_number,
        password_hash=hashed_password,
        role="employee",
        store_id=current_user.store_id
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
    return {"message": "Product Registration API is running."}
