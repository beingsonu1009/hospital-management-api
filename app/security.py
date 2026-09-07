from pwdlib import PasswordHash


# PasswordHash automatically manages secure password hashing
# and password verification.
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Convert a plain password into a secure password hash.
    """
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Check whether the entered password matches the stored hash.
    """
    return password_hash.verify(password, hashed_password)

from datetime import datetime, timedelta, timezone
import os

from dotenv import load_dotenv
from jose import jwt
from pwdlib import PasswordHash


load_dotenv()



# PASSWORD HASHING


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Plain password ko secure hash mein convert karta hai.
    """
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Entered password ko stored hash ke against verify karta hai.
    """
    return password_hash.verify(password, hashed_password)


# JWT CONFIGURATION

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

JWT_ALGORITHM = "HS256"

# Access token kitne minutes valid rahega.
ACCESS_TOKEN_EXPIRE_MINUTES = 30



# JWT CREATION


def create_access_token(data: dict) -> str:
    """
    JWT access token create karta hai.
    """

    # Original data ko copy kar rahe hain taaki
    # caller ka dictionary directly modify na ho.
    to_encode = data.copy()

    # Token ki expiration time calculate kar rahe hain.
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # JWT payload mein expiration claim add kar rahe hain.
    to_encode.update({
        "exp": expire
    })

    # JWT ko secret key + algorithm ke saath sign karte hain.
    encoded_jwt = jwt.encode(
        to_encode,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return encoded_jwt