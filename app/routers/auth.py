from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.auth import hash_password, verify_password, create_access_token


router = APIRouter(
    prefix = "/auth",
    tags = ["auth"]
)

@router.post("/register", response_model = schemas.UserResponse)
def register_user(
    user_request: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(models.User.username == user_request.username).first()

    if existing_user:
        raise HTTPException(
            status_code = 400,
            detail = "Username already exists"
        )
    
    user = models.User(
        username = user_request.username,
        email = user_request.email,
        hashed_password = hash_password(user_request.password),
        role = user_request.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid credentials"
        )
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code = 401,
            detail = "Invalid credentials"
        )

    token = create_access_token(
    username = user.username,
    user_id = user.id,
    role = user.role
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role
    }