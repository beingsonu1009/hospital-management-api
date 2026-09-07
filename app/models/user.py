from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    # Unique ID for every user
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Username used to identify/login the user
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    # NEVER store the actual password
    # Only the password hash will be stored
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Account status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="Active"
    )