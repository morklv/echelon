from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext

from dotenv import load_dotenv
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app import models


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise RuntimeError("SECRET_KEY is not set")

ALGORITHM = os.getenv("ALGORITHM")
if ALGORITHM is None:
    raise RuntimeError("ALGORITHM is not set")


ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
if ACCESS_TOKEN_EXPIRE_MINUTES is None:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES is not set")
ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)



bcrypt_context = CryptContext(
    schemes = ["bcrypt"],
    deprecated = "auto"
)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl = "/auth/login")


def hash_password(password: str):
    return bcrypt_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt_context.verify(
        plain_password,
        hashed_password
    )

def create_access_token(username: str, user_id: int, role: str):
    encode = {
        "sub": username,
        "id": user_id,
        "role": role
    }

    expires = datetime.now(timezone.utc) + timedelta(
        minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    )

    encode.update({
        "exp": expires
    })

    return jwt.encode(
        encode,
        SECRET_KEY,
        algorithm = ALGORITHM
    )

def get_current_user(
    token: str = Depends(oauth2_bearer),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms = [ALGORITHM]
        )

        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")

        if username is None or user_id is None:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid authentification credentials"
            )

    except JWTError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid authentication credentials"
        )
    
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "User not found"
        )
        
    return user