"""
Doctor database model.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Doctor(Base):
    """
    Doctor table ka SQLAlchemy model.
    """

    __tablename__ = "doctor"

    # Doctor ki unique ID
    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # Doctor ka naam
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Doctor ki specialisation
    specialisation: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    # Doctor ka phone number
    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    # Doctor ka account/status
    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Active"
    )

    # Ek doctor ke multiple working-hours records ho sakte hain.
    #
    # Doctor delete hone par uske working-hours records
    # bhi automatically handle honge.
    working_hours: Mapped[list["DoctorWorkingHours"]] = relationship(
        "DoctorWorkingHours",
        back_populates="doctor",
        cascade="all, delete-orphan"
    )