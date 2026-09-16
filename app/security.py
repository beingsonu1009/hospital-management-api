# =========================================================
# app/security.py
# Password hashing + JWT authentication
# =========================================================

import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# PASSWORD HASHING
# =========================================================

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Plain password ko secure hash mein convert karta hai.
    """
    return password_hash.hash(password)


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    """
    Entered password ko stored hash ke against verify karta hai.
    """
    return password_hash.verify(
        password,
        hashed_password,
    )


# =========================================================
# JWT CONFIGURATION
# =========================================================

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


# =========================================================
# JWT TOKEN CREATE
# =========================================================

def create_access_token(data: dict) -> str:
    """
    User information ke basis par JWT token create karta hai.
    """

    # Original data ki copy banao.
    to_encode = data.copy()

    # Token expiry time calculate karo.
    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    # JWT mein expiry add karo.
    to_encode.update(
        {
            "exp": expire,
        }
    )

    # JWT token generate karo.
    encoded_jwt = jwt.encode(
        to_encode,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    return encoded_jwt


# =========================================================
# HTTP BEARER
# =========================================================

# Frontend request se:
# Authorization: Bearer <token>
# token read karne ke liye use hoga.
bearer_scheme = HTTPBearer()


# =========================================================
# CURRENT USER
# =========================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
):
    """
    JWT token ko verify karta hai.

    Valid token:
        request continue

    Invalid / expired token:
        401 Unauthorized
    """

    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:
        # JWT decode + signature verification.
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )

        # Login ke time humne user id 'sub' mein save ki thi.
        user_id = payload.get("sub")

        # Token mein sub nahi hai to token invalid hai.
        if user_id is None:
            raise credentials_exception

        return user_id

    except JWTError:
        # Invalid signature / expired token / malformed token.
        raise credentials_exception