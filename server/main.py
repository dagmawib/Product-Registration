from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, database
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
import logging
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Utility functions for password hashing and JWT
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    from datetime import datetime, timedelta
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.SessionLocal)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = db.query(models.User).filter(models.User.username == username).first()
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
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
    # Employee sales history
    sales = db.query(models.Sale, models.User.username).join(models.User, models.Sale.user_id == models.User.id).join(models.Product, models.Sale.product_id == models.Product.id).filter(models.Product.store_id == current_user.store_id).all()
    employee_sales = {}
    for sale, username in sales:
        if username not in employee_sales:
            employee_sales[username] = 0
        employee_sales[username] += sale.quantity
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

@app.post("/auth/register_admin", response_model=schemas.UserOut)
def register_admin(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Create store and admin user
    store = models.Store(name=user.store_name)
    db.add(store)
    db.commit()
    db.refresh(store)
    hashed_password = get_password_hash(user.password)
    admin = models.User(
        username=user.username,
        password_hash=hashed_password,
        role="admin",
        store_id=store.id
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return schemas.UserOut(
        id=admin.id,
        username=admin.username,
        role=admin.role,
        store_id=admin.store_id
    )

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/add_employee", response_model=schemas.UserOut)
def add_employee(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    if user.role != "employee":
        raise HTTPException(status_code=400, detail="Role must be 'employee'")
    hashed_password = get_password_hash(user.password)
    employee = models.User(
        username=user.username,
        password_hash=hashed_password,
        role="employee",
        store_id=current_user.store_id
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return schemas.UserOut(
        id=employee.id,
        username=employee.username,
        role=employee.role,
        store_id=employee.store_id
    )

@app.get("/")
def root():
    return {"message": "Product Registration API is running."}
