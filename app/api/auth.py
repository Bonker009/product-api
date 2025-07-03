from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import authenticate_user, create_access_token, get_current_active_user
from app.crud import create_user, get_user_by_email, get_user_by_username
from app.schemas import User, UserCreate, Token, Login
from app.config import settings

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: Valid email address
    - **username**: 3-100 characters, alphanumeric and underscore only
    - **password**: 8-100 characters, must contain uppercase, lowercase, and digit
    - **full_name**: Optional full name
    """
    return create_user(db=db, user=user)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login to get access token.
    
    - **username**: Username or email
    - **password**: User password
    """
    # Try to authenticate with username first, then email
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Try with email
        user_by_email = get_user_by_email(db, form_data.username)
        if user_by_email:
            user = authenticate_user(db, str(user_by_email.username), form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not bool(user.is_active):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information.
    """
    return current_user


@router.post("/login-alt", response_model=Token)
def login_alt(login_data: Login, db: Session = Depends(get_db)):
    """
    Alternative login endpoint using JSON body instead of form data.
    
    - **username**: Username or email
    - **password**: User password
    """
    # Try to authenticate with username first, then email
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        # Try with email
        user_by_email = get_user_by_email(db, login_data.username)
        if user_by_email:
            user = authenticate_user(db, str(user_by_email.username), login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"} 