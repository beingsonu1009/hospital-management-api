"""
Doctor Working Hours database model.

Is table mein doctor ke weekly working hours store honge.
"""

from datetime import time

from sqlalchemy import ForeignKey, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DoctorWorkingHours(Base):
    """
    Doctor ke working hours ka SQLAlchemy model.
    """

    __tablename__ = "doctor_working_hours"

    # Working-hours record ki unique ID
    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # Doctor ki ID
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey(
            "doctor.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    # Day:
    # 1 = Monday
    # 2 = Tuesday
    # ...
    # 7 = Sunday
    day_of_week: Mapped[int] = mapped_column(
        nullable=False
    )

    # Doctor ka working start time
    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    # Doctor ka working end time
    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    # Doctor ke saath relationship
    doctor: Mapped["Doctor"] = relationship(
        "Doctor",
        back_populates="working_hours"
    )

    # Ek doctor ke same day par sirf ek working-hours record.
    __table_args__ = (
        UniqueConstraint(
            "doctor_id",
            "day_of_week",
            name="uq_doctor_working_day"
        ),
    )