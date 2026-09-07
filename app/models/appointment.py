from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Appointment(Base):
    __tablename__ = "appointment"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    # Patient table ki id ko reference karega
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patient.id"),
        nullable=False
    )

    # Doctor table ki id ko reference karega
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctor.id"),
        nullable=False
    )

    # Appointment kab hai
    appointment_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    # Appointment kis reason ke liye hai
    reason: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Example: Scheduled / Completed / Cancelled
    status: Mapped[str] = mapped_column(
        String(100),
        default="Scheduled"
    )
    