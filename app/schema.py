# =========================================================
# app/schema.py
# Pydantic schemas
# =========================================================

from datetime import date, time

from pydantic import BaseModel, Field, model_validator


# =========================================================
# PATIENT SCHEMAS
# =========================================================

class PatientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., min_length=1, max_length=20)
    disease: str = Field(..., min_length=1, max_length=255)


class PatientResponse(PatientCreate):
    id: int

    model_config = {
        "from_attributes": True
    }


# =========================================================
# DOCTOR SCHEMAS
# =========================================================

class DoctorCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    specialisation: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=7, max_length=20)
    status: str = Field(default="Active", max_length=100)


class DoctorResponse(DoctorCreate):
    id: int

    model_config = {
        "from_attributes": True
    }


# =========================================================
# DOCTOR WORKING HOURS SCHEMAS
# =========================================================

class WorkingHoursCreate(BaseModel):
    # 1 = Monday ... 7 = Sunday
    day_of_week: int = Field(..., ge=1, le=7)

    start_time: time
    end_time: time

    @model_validator(mode="after")
    def validate_working_hours(self):
        # Start time hamesha end time se pehle hona chahiye.
        if self.start_time >= self.end_time:
            raise ValueError(
                "start_time must be before end_time"
            )

        return self


class WorkingHoursResponse(WorkingHoursCreate):
    id: int
    doctor_id: int

    model_config = {
        "from_attributes": True
    }


# =========================================================
# APPOINTMENT SCHEMAS
# =========================================================

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int

    appointment_date: date
    start_time: time

    # Duration minutes mein hogi.
    duration: int = Field(..., gt=0)

    reason: str = Field(
        ...,
        min_length=3,
        max_length=255
    )

    status: str = "Scheduled"


class AppointmentResponse(AppointmentCreate):
    id: int

    model_config = {
        "from_attributes": True
    }


class AppointmentReschedule(BaseModel):
    appointment_date: date
    start_time: time
    duration: int = Field(..., gt=0)


# =========================================================
# USER / AUTH SCHEMAS
# =========================================================

class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=100
    )

    password: str = Field(
        ...,
        min_length=6,
        max_length=100
    )


class UserResponse(BaseModel):
    id: int
    username: str

    model_config = {
        "from_attributes": True
    }


class UserLogin(BaseModel):
    username: str
    password: str


# =========================================================
# TOKEN SCHEMA
# =========================================================

class Token(BaseModel):
    access_token: str
    token_type: str