"""
User database model.

Is table mein application users ki login information store hoti hai.
Password plain text mein store nahi hoga; hashed password database mein
store hoga.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """
    Users table ka SQLAlchemy model.
    """

    __tablename__ = "users"

    # User ki unique ID
    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # Login username
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    # Database mein existing column ka exact naam: hashed_password
    # Isliye Python attribute bhi hashed_password rakha gaya hai.
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # User ka status — existing database column
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active"
    )