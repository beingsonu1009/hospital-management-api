from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field



# PATIENT SCHEMAS


class PatientCreate(BaseModel):
    # Patient ka naam: minimum 3 aur maximum 50 characters
    name: str = Field(..., min_length=3, max_length=50)

    # Age 1 se 120 ke beech honi chahiye
    age: int = Field(..., ge=1, le=120)

    # Gender sirf in 3 values mein se ek ho sakta hai
    gender: Literal["Male", "Female", "Other"]

    # Disease minimum 3 characters ki honi chahiye
    disease: str = Field(..., min_length=3)


class PatientResponse(PatientCreate):
    # Database se generated patient ID
    id: int

    # SQLAlchemy ORM object ko Pydantic response mein convert karne ke liye
    model_config = {
        "from_attributes": True
    }



# DOCTOR SCHEMAS


class DoctorCreate(BaseModel):
    name: str
    specialisation: str
    phone: str

    # Agar status nahi diya gaya to Active hoga
    status: str = "Active"


class DoctorResponse(DoctorCreate):
    # Database se generated doctor ID
    id: int

    # SQLAlchemy ORM object se response create karne ke liye
    model_config = {
        "from_attributes": True
    }



# APPOINTMENT SCHEMAS


class AppointmentCreate(BaseModel):
    # Kis patient ke saath appointment hai
    patient_id: int

    # Kis doctor ke saath appointment hai
    doctor_id: int

    # Appointment ki date aur time
    appointment_date: datetime

    # Appointment ka reason
    reason: str = Field(
        ...,
        min_length=3,
        max_length=255
    )

    # Agar status nahi diya gaya to Scheduled hoga
    status: str = "Scheduled"


class AppointmentResponse(AppointmentCreate):
    # Database se generated appointment ID
    id: int

    # SQLAlchemy ORM object ko Pydantic response mein convert karne ke liye
    model_config = {
        "from_attributes": True
    }

    # 
# USER / AUTHENTICATION SCHEMAS
# 

class UserCreate(BaseModel):
    # User ka login username
    username: str = Field(
        ...,
        min_length=3,
        max_length=100
    )

    # Plain password sirf request ke time receive hoga.
    # Database mein ye password directly store nahi hoga.
    password: str = Field(
        ...,
        min_length=8,
        max_length=128
    )


class UserResponse(BaseModel):
    # Database se generated user ID
    id: int

    # User ka username
    username: str

    # Account status
    status: str

    # SQLAlchemy ORM object ko Pydantic response mein
    # convert karne ke liye
    model_config = {
        "from_attributes": True
    }


class UserLogin(BaseModel):
    # Login ke waqt username receive hoga
    username: str

    # Login ke waqt password receive hoga
    password: str