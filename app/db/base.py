"""
SQLAlchemy Base configuration.

Is file mein saare database models ke liye common Base class define hoti hai.
"""

from sqlalchemy.orm import DeclarativeBase

# SQLAlchemy Base
class Base(DeclarativeBase):
    """
    Saare SQLAlchemy models isi Base ko inherit karenge.

    Example:
        class Patient(Base):
            ...
    """

    pass