from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_active_user, get_current_superuser
from app.crud import get_users, get_user, update_user, delete_user
from app.schemas import User, UserUpdate, Message
from app.models import User as UserModel

router = APIRouter()


@router.get("/", response_model=List[User])
def read_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser)
):
    """
    Retrieve all users with pagination.
    Only accessible by superusers.
    """
    users = get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser)
):
    """
    Get a specific user by ID.
    Only accessible by superusers.
    """
    user = get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=User)
def update_existing_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser)
):
    """
    Update an existing user.
    Only accessible by superusers.
    """
    return update_user(db=db, user_id=user_id, user_update=user_update)


@router.delete("/{user_id}", response_model=Message)
def delete_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_superuser)
):
    """
    Delete a user.
    Only accessible by superusers.
    """
    # Prevent superuser from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    delete_user(db=db, user_id=user_id)
    return {"message": "User deleted successfully"} 