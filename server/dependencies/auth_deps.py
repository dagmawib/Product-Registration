\
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import logging

from .. import database, models
from ..core import config
from ..auth_utils import security # For verify_password, get_password_hash, create_access_token

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login_admin", auto_error=False) # auto_error=False to handle token manually

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if token is None: # Handle case where token is not provided (due to auto_error=False)
        logger.warning("No token provided for authentication.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        sub: str = payload.get("sub")
        role: str = payload.get("role")
        user_id: int = payload.get("id")

        if sub is None or role is None or user_id is None:
            logger.warning(f"Token missing sub, role, or id. Payload: {payload}")
            raise credentials_exception
        
        user = None
        # Fetch user by ID and verify role from token matches DB role for extra security
        db_user = db.query(models.User).filter(models.User.id == user_id).first()

        if not db_user:
            logger.warning(f"User with id {user_id} not found in DB.")
            raise credentials_exception
        
        # Verify subject and role from token match the user found in DB
        # For admin, sub is email. For employee, sub can be username or email.
        # The critical part is that the user_id from token fetches a valid user,
        # and that user's role in DB matches the role in token.
        if db_user.role != role:
            logger.warning(f"Token role {role} does not match DB role {db_user.role} for user id {user_id}.")
            raise credentials_exception

        # Further check if 'sub' matches expected identifier for that role
        if role == "admin" and db_user.email != sub:
            logger.warning(f"Admin token sub {sub} does not match DB email {db_user.email} for user id {user_id}.")
            raise credentials_exception
        # Add similar check for employee if 'sub' for employee token is standardized (e.g., username)
        # elif role == "employee" and db_user.username != sub: # Assuming employee uses username as sub
        #     logger.warning(f"Employee token sub {sub} does not match DB username {db_user.username} for user id {user_id}.")
        #     raise credentials_exception
            
        return db_user # Return the user model instance
    except JWTError as e:
        logger.error(f"JWTError decoding token: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}")
        raise credentials_exception

def admin_required(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        logger.warning(f"Admin access denied for user: {current_user.email if hasattr(current_user, 'email') else current_user.id} with role {current_user.role}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted: Admin access required")
    return current_user

def employee_required(current_user: models.User = Depends(get_current_user)):
    # Allows admin or employee
    if current_user.role not in ["employee", "admin"]:
        logger.warning(f"Employee access denied for user: {current_user.email if hasattr(current_user, 'email') else current_user.id} with role {current_user.role}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted: Employee or Admin access required")
    return current_user

def current_user_or_admin_required(user_id_in_path: int, current_user: models.User = Depends(get_current_user)):
    if current_user.role == "admin":
        return current_user
    if current_user.id != user_id_in_path:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted: Access denied")
    return current_user
