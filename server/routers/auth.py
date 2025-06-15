\
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm # Added back this import
from sqlalchemy.orm import Session
from typing import Any, Optional, Union # Added Union

import schemas
import models
import database
from dependencies import auth_deps
from auth_utils import security
from core import config
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

@router.post("/register_admin", response_model=schemas.AdminOut, status_code=status.HTTP_201_CREATED) # Changed response_model to AdminOut
async def register_admin_and_store(
    admin_data: schemas.AdminStoreRegister,
    db: Session = Depends(auth_deps.get_db)
):
    logger.info(f"Admin registration attempt for email: {admin_data.email} and store: {admin_data.store_name}")

    existing_store_by_name = db.query(models.Store).filter(models.Store.name == admin_data.store_name).first()
    if existing_store_by_name:
        logger.warning(f"Admin registration failed. Store name already exists: {admin_data.store_name}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Store name already registered.")
    
    existing_user_by_email = db.query(models.User).filter(models.User.email == admin_data.email).first()
    if existing_user_by_email:
        logger.warning(f"Admin registration failed. Email already registered: {admin_data.email}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

    # Create the store first
    new_store = models.Store(
        name=admin_data.store_name,
    )
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    logger.info(f"Store created successfully: {new_store.name} with ID: {new_store.id}")

    # Now create the admin user
    hashed_password = security.get_password_hash(admin_data.password)
    
    # Ensure all fields expected by models.User are present and correctly named
    new_admin_data = {
        "email": admin_data.email,
        "hashed_password": hashed_password,
        "role": "admin",
        "store_id": new_store.id,
        "store_name": new_store.name, # This should align with your User model field for store name
        "first_name": admin_data.first_name,
        "last_name": admin_data.last_name,
        "phone_number": admin_data.phone_number
    }
    new_admin = models.User(**new_admin_data)
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    logger.info(f"Admin user created successfully: {new_admin.email} for store ID: {new_store.id}")
    
    # Return AdminOut schema
    return schemas.AdminOut(
        id=new_admin.id,
        email=new_admin.email,
        first_name=new_admin.first_name,
        last_name=new_admin.last_name,
        phone_number=new_admin.phone_number,
        store_name=new_store.name, # Use the actual store name from the created store object
        role=new_admin.role,
        store_id=new_admin.store_id
    )


@router.post("/add_employee", response_model=schemas.EmployeeOut, status_code=status.HTTP_201_CREATED) # Changed to EmployeeOut
async def add_employee(
    employee_data: schemas.EmployeeCreate, # Changed from UserCreate to EmployeeCreate for clarity
    db: Session = Depends(auth_deps.get_db),
    current_admin: models.User = Depends(auth_deps.admin_required)
):
    logger.info(f"Attempting to add employee by admin: {current_admin.email}")
    # Note: EmployeeCreate doesn't have an email field. Employees might not have emails.
    # If employees can have emails and they should be unique, add email to EmployeeCreate and check for existing.

    hashed_password = security.get_password_hash(employee_data.password)
    
    new_employee_data = {
        "first_name": employee_data.first_name,
        "last_name": employee_data.last_name,
        "hashed_password": hashed_password,
        "phone_number": employee_data.phone_number,
        "role": "employee", # Explicitly set role
        "store_id": current_admin.store_id, # Employee belongs to the admin's store
        "store_name": current_admin.store_name # Assign store_name from admin
    }
    
    new_employee = models.User(**new_employee_data)
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    logger.info(f"Employee added successfully: {new_employee.first_name} {new_employee.last_name} for store ID: {current_admin.store_id}")
    
    # Return EmployeeOut schema
    return schemas.EmployeeOut(
        id=new_employee.id,
        first_name=new_employee.first_name,
        last_name=new_employee.last_name,
        phone_number=new_employee.phone_number,
        role=new_employee.role,
        store_id=new_employee.store_id
    )

@router.get("/users/me", response_model=Union[schemas.AdminOut, schemas.EmployeeOut]) # Changed to Union of AdminOut and EmployeeOut
async def read_users_me(current_user: models.User = Depends(auth_deps.get_current_user)):
    logger.info(f"Fetching details for current user: {current_user.id} with role: {current_user.role}")
    # Pydantic will attempt to serialize current_user (models.User) into AdminOut or EmployeeOut
    # Ensure that the fields in models.User can correctly populate the respective Out schemas.
    # For example, if current_user.role == 'admin', it will try to fit into AdminOut.
    # If current_user.role == 'employee', it will try to fit into EmployeeOut.
    return current_user

# Example: Get a specific user's details (admin access or self access)
@router.get("/users/{user_id}", response_model=Union[schemas.AdminOut, schemas.EmployeeOut]) # Changed to Union
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
@router.get("/users", response_model=list[Union[schemas.AdminOut, schemas.EmployeeOut]]) # Changed response model
async def list_users(
    db: Session = Depends(auth_deps.get_db),
    current_admin: models.User = Depends(auth_deps.admin_required) # Ensures only admin can list users
):
    logger.info(f"Admin {current_admin.email} listing all users in their store.")
    # Filter users by the admin's store_id
    users = db.query(models.User).filter(models.User.store_id == current_admin.store_id).all()
    return users

# Placeholder for updating user (admin or self) - simplified
@router.put("/users/{user_id}", response_model=Union[schemas.AdminOut, schemas.EmployeeOut]) # Changed response model
async def update_user_details(
    user_id: int, 
    user_update: schemas.UserUpdate, # Using the new UserUpdate schema
    db: Session = Depends(auth_deps.get_db),
    requesting_user: models.User = Depends(auth_deps.get_current_user)
):
    logger.info(f"User {requesting_user.id} attempting to update details for user: {user_id}")

    user_to_update = db.query(models.User).filter(models.User.id == user_id).first()

    if not user_to_update:
        logger.warning(f"Update failed. User with id {user_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Authorization check: Admin can update any user in their store.
    # Non-admin (employee) can only update their own details.
    if requesting_user.role == "admin":
        if user_to_update.store_id != requesting_user.store_id:
            logger.warning(f"Admin {requesting_user.id} (store {requesting_user.store_id}) " 
                           f"attempted to update user {user_id} (store {user_to_update.store_id}) in another store.")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins can only update users within their own store.")
    elif requesting_user.id != user_id:
        logger.warning(f"User {requesting_user.id} attempted to update details for another user {user_id} without admin rights.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user's details")

    update_data = user_update.model_dump(exclude_unset=True)
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

