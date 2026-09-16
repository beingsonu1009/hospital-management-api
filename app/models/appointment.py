"""
Appointment database model.

Is model mein patient aur doctor ke appointments store hote hain.
"""

from datetime import date, time

from sqlalchemy import Date, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Appointment(Base):
    """
    Appointment table ka SQLAlchemy model.
    """

    __tablename__ = "appointment"

    # Appointment ki unique ID
    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # Patient ki ID
    patient_id: Mapped[int] = mapped_column(
        ForeignKey(
            "patient.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    # Doctor ki ID
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey(
            "doctor.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    # Appointment ki date
    appointment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    # Appointment ka starting time
    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    # Appointment duration minutes mein
    duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    # Appointment ka reason
    reason: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Appointment status
    # Example: Scheduled / Cancelled
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="Scheduled"
    )

    # Patient relationship
    patient: Mapped["Patient"] = relationship(
        "Patient"
    )

    # Doctor relationship
    doctor: Mapped["Doctor"] = relationship(
        "Doctor"
    )