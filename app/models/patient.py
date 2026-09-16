"""
Patient database model.

Is model ka table PostgreSQL mein "patient" naam se create hota hai.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Patient(Base):
    """
    Patient table ka SQLAlchemy model.
    """

    __tablename__ = "patient"

    # Patient ki unique ID
    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # Patient ka naam
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Patient ki age
    age: Mapped[int] = mapped_column(
        nullable=False
    )

    # Patient ka gender
    gender: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    # Patient ki disease
    disease: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )