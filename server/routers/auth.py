\
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm # Added back this import
from sqlalchemy.orm import Session
from typing import Any, Optional

from .. import schemas, models, database
from ..dependencies import auth_deps
from ..auth_utils import security
from ..core import config
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/login_admin", response_model=schemas.Token)
async def login_admin_for_access_token(admin_credentials: schemas.AdminLogin, db: Session = Depends(auth_deps.get_db)): # Changed from OAuth2PasswordRequestForm
    logger.info(f"Admin login attempt for email: {admin_credentials.email}") # Changed from form_data.username
    user = db.query(models.User).filter(models.User.email == admin_credentials.email, models.User.role == "admin").first() # Changed
    if not user or not security.verify_password(admin_credentials.password, user.hashed_password): # Changed from form_data.password
        logger.warning(f"Admin login failed for email: {admin_credentials.email}") # Changed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password", # Changed message slightly for clarity
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )
    logger.info(f"Admin login successful for email: {admin_credentials.email}") # Changed
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login_employee", response_model=schemas.Token)
async def login_employee_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(auth_deps.get_db)):
    logger.info(f"Employee login attempt for username: {form_data.username}")
    # Assuming employee username is stored in 'email' field for simplicity, or a dedicated 'username' field.
    # Adjust query if employees use a different field for login (e.g., models.User.username)
    user = db.query(models.User).filter(models.User.email == form_data.username, models.User.role == "employee").first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Employee login failed for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password for employee",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # For employee, 'sub' could be username or email. Ensure it's consistent with get_current_user.
    access_token = security.create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id} # Or user.username if that's the login identifier
    )
    logger.info(f"Employee login successful for username: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register_admin", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_admin_and_store(
    admin_data: schemas.AdminStoreRegister, # New schema needed for this
    db: Session = Depends(auth_deps.get_db)
):
    logger.info(f"Admin registration attempt for email: {admin_data.email} and store: {admin_data.store_name}")

    existing_store_by_name = db.query(models.Store).filter(models.Store.name == admin_data.store_name).first() # Changed storename to name
    if existing_store_by_name:
        logger.warning(f"Admin registration failed. Store name already exists: {admin_data.store_name}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Store name already registered.")
    
    existing_user_by_email = db.query(models.User).filter(models.User.email == admin_data.email).first()
    if existing_user_by_email:
        logger.warning(f"Admin registration failed. Email already registered: {admin_data.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    # Create the store first
    new_store = models.Store(
        name=admin_data.store_name, # Changed storename to name
    )
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    logger.info(f"Store created successfully: {new_store.name} with ID: {new_store.id}") # Changed storename to name

    # Now create the admin user
    hashed_password = security.get_password_hash(admin_data.password)
    
    admin_user_dict = {
        "email": admin_data.email,
        "hashed_password": hashed_password,
        "role": "admin",
        "store_id": new_store.id,
        "store_name": new_store.name, # Changed storename to name, store_name on User model still refers to the store's name
        "first_name": admin_data.first_name,
        "last_name": admin_data.last_name,
        "phone_number": admin_data.phone_number
    }
    
    # Ensure all fields in admin_user_dict are valid for models.User
    new_admin = models.User(**admin_user_dict)
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    logger.info(f"Admin user created successfully: {new_admin.email} for store ID: {new_store.id}")
    
    # Return UserResponse schema
    return new_admin


@router.post("/add_employee", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def add_employee(
    employee_data: schemas.UserCreate, 
    db: Session = Depends(auth_deps.get_db),
    current_admin: models.User = Depends(auth_deps.admin_required) # Ensures only admin can add employees
):
    logger.info(f"Attempting to add employee: {employee_data.email} by admin: {current_admin.email}")
    db_user = db.query(models.User).filter(models.User.email == employee_data.email).first()
    if db_user:
        logger.warning(f"Failed to add employee. Email already registered: {employee_data.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = security.get_password_hash(employee_data.password)
    
    # Ensure role is explicitly set to 'employee' if not provided or to prevent misuse
    # For this endpoint, we are adding an employee, so role should be 'employee'.
    # The UserCreate schema might or might not have a 'role' field.
    # If it does, it should be validated or overridden here.
    # If UserCreate doesn't have 'role', we set it.
    
    # Create a dictionary for user creation, ensuring role is 'employee'
    user_dict = employee_data.model_dump()
    user_dict['hashed_password'] = hashed_password
    user_dict['role'] = 'employee' # Explicitly set role

    # If UserCreate schema includes fields not in User model (like 'password'), exclude them
    # Or ensure User model can handle them (e.g. by not mapping 'password' directly)
    # For UserCreate, 'password' is fine, but when creating models.User, we use 'hashed_password'
    
    # Create user model instance
    # We need to ensure that only fields defined in models.User are passed.
    # UserCreate might have 'password', models.User has 'hashed_password'.
    # UserCreate might have 'store_name', 'first_name', 'last_name' which should be in models.User.

    new_employee = models.User(
        email=user_dict['email'],
        hashed_password=user_dict['hashed_password'],
        role=user_dict['role'],
        store_name=user_dict.get('store_name'), # Assuming UserCreate and models.User have these
        first_name=user_dict.get('first_name'),
        last_name=user_dict.get('last_name')
    )
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    logger.info(f"Employee added successfully: {new_employee.email}")
    return new_employee

@router.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(auth_deps.get_current_user)):
    logger.info(f"Fetching details for current user: {current_user.id}")
    return current_user

# Example: Get a specific user's details (admin access or self access)
@router.get("/users/{user_id}", response_model=schemas.UserResponse)
async def read_user(
    user_id: int, 
    db: Session = Depends(auth_deps.get_db), 
    # current_user: models.User = Depends(auth_deps.get_current_user) # Basic auth
    # More specific: current_user_or_admin_required dependency
    # For this, we need to pass user_id to the dependency. FastAPI doesn't support this directly in Depends.
    # So, we'll do the check inside the endpoint.
    requesting_user: models.User = Depends(auth_deps.get_current_user)
):
    logger.info(f"User {requesting_user.id} attempting to fetch details for user: {user_id}")
    if requesting_user.role != "admin" and requesting_user.id != user_id:
        logger.warning(f"Access denied for user {requesting_user.id} to view user {user_id} details.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        logger.warning(f"User with id {user_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logger.info(f"Successfully fetched details for user: {user_id}")
    return user

# Placeholder for listing users (admin only)
@router.get("/users", response_model=list[schemas.UserResponse])
async def list_users(
    db: Session = Depends(auth_deps.get_db),
    current_admin: models.User = Depends(auth_deps.admin_required) # Ensures only admin can list users
):
    logger.info(f"Admin {current_admin.email} listing all users.")
    users = db.query(models.User).all()
    return users

# Placeholder for updating user (admin or self) - simplified
@router.put("/users/{user_id}", response_model=schemas.UserResponse)
async def update_user_details(
    user_id: int, 
    user_update: schemas.UserUpdate, # A new schema for updates, might exclude role, password
    db: Session = Depends(auth_deps.get_db),
    requesting_user: models.User = Depends(auth_deps.get_current_user)
):
    logger.info(f"User {requesting_user.id} attempting to update details for user: {user_id}")
    
    user_to_update = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_update:
        logger.warning(f"User with id {user_id} not found for update.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if requesting_user.role != "admin" and requesting_user.id != user_id:
        logger.warning(f"Access denied for user {requesting_user.id} to update user {user_id} details.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")

    update_data = user_update.model_dump(exclude_unset=True) # Get only provided fields

    # Prevent non-admins from changing role
    if 'role' in update_data and requesting_user.role != "admin":
        logger.warning(f"User {requesting_user.id} (not admin) attempted to change role for user {user_id}.")
        del update_data['role'] # Or raise HTTPException

    # Password update should be handled separately, e.g., via a /users/{user_id}/change-password endpoint
    if 'password' in update_data: # Assuming UserUpdate might contain password for change
        logger.info(f"Password change requested for user {user_id}. This should be a dedicated endpoint.")
        # For now, let's hash it if provided, but ideally, this is a separate flow.
        # This is a simplified example; production password changes need more care (e.g. current password verification)
        user_to_update.hashed_password = security.get_password_hash(update_data['password'])
        del update_data['password'] # Remove so it's not processed by the loop below

    for key, value in update_data.items():
        setattr(user_to_update, key, value)
    
    db.commit()
    db.refresh(user_to_update)
    logger.info(f"Successfully updated details for user: {user_id}")
    return user_to_update

# Placeholder for deleting user (admin only)
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    user_id: int,
    db: Session = Depends(auth_deps.get_db),
    current_admin: models.User = Depends(auth_deps.admin_required)
):
    logger.info(f"Admin {current_admin.email} attempting to delete user: {user_id}")
    user_to_delete = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_delete:
        logger.warning(f"User with id {user_id} not found for deletion.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Prevent admin from deleting themselves? Or other critical checks.
    if user_to_delete.id == current_admin.id:
         logger.warning(f"Admin {current_admin.email} attempted to delete their own account.")
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admins cannot delete their own account.")

    db.delete(user_to_delete)
    db.commit()
    logger.info(f"Successfully deleted user: {user_id}")
    return None # FastAPI will return 204 No Content

