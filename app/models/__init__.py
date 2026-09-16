"""
Models package.

Yahan saare database models import kiye ja rahe hain
taaki SQLAlchemy ko application ke saare models ka pata rahe.
"""

from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import User
from app.models.working_hr import DoctorWorkingHours


__all__ = [
    "Appointment",
    "Doctor",
    "Patient",
    "User",
    "DoctorWorkingHours",
]