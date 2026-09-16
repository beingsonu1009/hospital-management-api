# =========================================================
# app/routers/appoinment.py
# Appointment CRUD + Scheduling Rules + JWT Protection
# =========================================================

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.working_hr import DoctorWorkingHours
from app.schema import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentReschedule,
)
from app.security import get_current_user


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
    # Appointment ke saare endpoints ke liye JWT required hai.
    dependencies=[Depends(get_current_user)],
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_appointment_start(
    appointment_date,
    start_time,
):
    # Date + time ko ek single datetime mein convert karo.
    return datetime.combine(
        appointment_date,
        start_time,
    )


def get_appointment_end(
    appointment_date,
    start_time,
    duration,
):
    # Start datetime calculate karo.
    start_datetime = get_appointment_start(
        appointment_date,
        start_time,
    )

    # Duration minutes add karke end datetime nikalo.
    return start_datetime + timedelta(
        minutes=duration,
    )


# =========================================================
# APPOINTMENT SLOT VALIDATION
# =========================================================

async def validate_appointment_slot(
    appointment_date,
    start_time,
    duration,
    doctor_id,
    db,
    exclude_appointment_id=None,
):
    """
    Booking/rescheduling se pehle appointment slot ki
    saari business rules validate karta hai.
    """

    # -----------------------------------------------------
    # 1. Past appointment check
    # -----------------------------------------------------

    appointment_start = get_appointment_start(
        appointment_date,
        start_time,
    )

    # Current datetime ke past mein booking allowed nahi hai.
    if appointment_start <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment cannot be booked in the past",
        )


    # -----------------------------------------------------
    # 2. Appointment end calculate karo
    # -----------------------------------------------------

    appointment_end = get_appointment_end(
        appointment_date,
        start_time,
        duration,
    )


    # -----------------------------------------------------
    # 3. Doctor ke working hours find karo
    # -----------------------------------------------------

    # Python:
    # Monday = 0
    # Sunday = 6
    #
    # Database:
    # Monday = 1
    # Sunday = 7

    day_of_week = appointment_date.weekday() + 1

    working_hours_query = select(
        DoctorWorkingHours
    ).where(
        DoctorWorkingHours.doctor_id == doctor_id,
        DoctorWorkingHours.day_of_week == day_of_week,
    )

    working_hours_result = await db.execute(
        working_hours_query,
    )

    working_hours = (
        working_hours_result
        .scalar_one_or_none()
    )

    if working_hours is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor is not available on this day",
        )


    # -----------------------------------------------------
    # 4. Working hours ke andar appointment hai?
    # -----------------------------------------------------

    if (
        start_time < working_hours.start_time
        or appointment_end.time() > working_hours.end_time
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Appointment must be within doctor's "
                f"working hours "
                f"({working_hours.start_time} - "
                f"{working_hours.end_time})"
            ),
        )


    # -----------------------------------------------------
    # 5. Existing appointments find karo
    # -----------------------------------------------------

    existing_query = select(
        Appointment
    ).where(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.status != "Cancelled",
    )

    # Reschedule/update mein current appointment ko
    # conflict check se exclude karna hai.
    if exclude_appointment_id is not None:
        existing_query = existing_query.where(
            Appointment.id != exclude_appointment_id,
        )

    existing_result = await db.execute(
        existing_query,
    )

    existing_appointments = (
        existing_result
        .scalars()
        .all()
    )


    # -----------------------------------------------------
    # 6. Overlap check
    # -----------------------------------------------------

    for existing in existing_appointments:

        existing_start = get_appointment_start(
            existing.appointment_date,
            existing.start_time,
        )

        existing_end = get_appointment_end(
            existing.appointment_date,
            existing.start_time,
            existing.duration,
        )

        # Overlap tab hota hai:
        #
        # New Start < Existing End
        # AND
        # New End > Existing Start

        if (
            appointment_start < existing_end
            and appointment_end > existing_start
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Doctor already has an appointment "
                    "during this time"
                ),
            )


# =========================================================
# CREATE APPOINTMENT
# =========================================================

@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_appointment(
    appointment: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
):

    # -----------------------------------------------------
    # Patient existence check
    # -----------------------------------------------------

    patient_query = select(Patient).where(
        Patient.id == appointment.patient_id,
    )

    patient_result = await db.execute(
        patient_query,
    )

    patient = patient_result.scalar_one_or_none()

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )


    # -----------------------------------------------------
    # Doctor existence check
    # -----------------------------------------------------

    doctor_query = select(Doctor).where(
        Doctor.id == appointment.doctor_id,
    )

    doctor_result = await db.execute(
        doctor_query,
    )

    doctor = doctor_result.scalar_one_or_none()

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )


    # -----------------------------------------------------
    # Race condition protection
    # -----------------------------------------------------

    # Same doctor + same date ki simultaneous bookings
    # ko serialize karne ke liye PostgreSQL transaction lock.
    #
    # appointment_date.toordinal() date ko stable integer
    # lock key mein convert karta hai.

    await db.execute(
        text(
            """
            SELECT pg_advisory_xact_lock(
                :doctor_id,
                :appointment_date_key
            )
            """
        ),
        {
            "doctor_id": appointment.doctor_id,
            "appointment_date_key": (
                appointment.appointment_date.toordinal()
            ),
        },
    )


    # Lock milne ke baad slot validate karo.
    await validate_appointment_slot(
        appointment_date=appointment.appointment_date,
        start_time=appointment.start_time,
        duration=appointment.duration,
        doctor_id=appointment.doctor_id,
        db=db,
    )


    # -----------------------------------------------------
    # Appointment create
    # -----------------------------------------------------

    new_appointment = Appointment(
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date,
        start_time=appointment.start_time,
        duration=appointment.duration,
        reason=appointment.reason,
        status="Scheduled",
    )

    db.add(new_appointment)

    await db.commit()
    await db.refresh(new_appointment)

    return new_appointment


# =========================================================
# GET ALL APPOINTMENTS
# =========================================================

@router.get(
    "/",
    response_model=list[AppointmentResponse],
)
async def get_appointments(
    db: AsyncSession = Depends(get_db),
):

    query = select(
        Appointment
    ).order_by(
        Appointment.appointment_date,
        Appointment.start_time,
        Appointment.id,
    )

    result = await db.execute(query)

    return result.scalars().all()


# =========================================================
# GET ONE APPOINTMENT
# =========================================================

@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
async def get_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
):

    query = select(Appointment).where(
        Appointment.id == appointment_id,
    )

    result = await db.execute(query)

    appointment = result.scalar_one_or_none()

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )

    return appointment


# =========================================================
# UPDATE APPOINTMENT
# =========================================================

@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
async def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
):

    # -----------------------------------------------------
    # Existing appointment find karo
    # -----------------------------------------------------

    query = select(Appointment).where(
        Appointment.id == appointment_id,
    )

    result = await db.execute(query)

    appointment = result.scalar_one_or_none()

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )


    # Cancelled appointment ko update nahi karenge.
    if appointment.status == "Cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancelled appointment cannot be updated",
        )


    # -----------------------------------------------------
    # Patient existence check
    # -----------------------------------------------------

    patient_query = select(Patient).where(
        Patient.id == appointment_data.patient_id,
    )

    patient_result = await db.execute(
        patient_query,
    )

    patient = patient_result.scalar_one_or_none()

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )


    # -----------------------------------------------------
    # Doctor existence check
    # -----------------------------------------------------

    doctor_query = select(Doctor).where(
        Doctor.id == appointment_data.doctor_id,
    )

    doctor_result = await db.execute(
        doctor_query,
    )

    doctor = doctor_result.scalar_one_or_none()

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )


    # -----------------------------------------------------
    # Race condition protection
    # -----------------------------------------------------

    await db.execute(
        text(
            """
            SELECT pg_advisory_xact_lock(
                :doctor_id,
                :appointment_date_key
            )
            """
        ),
        {
            "doctor_id": appointment_data.doctor_id,
            "appointment_date_key": (
                appointment_data.appointment_date.toordinal()
            ),
        },
    )


    # -----------------------------------------------------
    # New slot validate karo
    # -----------------------------------------------------

    await validate_appointment_slot(
        appointment_date=appointment_data.appointment_date,
        start_time=appointment_data.start_time,
        duration=appointment_data.duration,
        doctor_id=appointment_data.doctor_id,
        db=db,
        exclude_appointment_id=appointment_id,
    )


    # -----------------------------------------------------
    # Appointment update
    # -----------------------------------------------------

    appointment.patient_id = appointment_data.patient_id
    appointment.doctor_id = appointment_data.doctor_id
    appointment.appointment_date = appointment_data.appointment_date
    appointment.start_time = appointment_data.start_time
    appointment.duration = appointment_data.duration
    appointment.reason = appointment_data.reason
    appointment.status = appointment_data.status

    await db.commit()
    await db.refresh(appointment)

    return appointment


# =========================================================
# CANCEL APPOINTMENT
# =========================================================

@router.post(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
)
async def cancel_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
):

    query = select(Appointment).where(
        Appointment.id == appointment_id,
    )

    result = await db.execute(query)

    appointment = result.scalar_one_or_none()

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )


    if appointment.status == "Cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment is already cancelled",
        )


    # Cancel karne par slot automatically free ho jayega
    # kyunki overlap query Cancelled records ko ignore karti hai.
    appointment.status = "Cancelled"

    await db.commit()
    await db.refresh(appointment)

    return appointment


# =========================================================
# RESCHEDULE APPOINTMENT
# =========================================================

@router.post(
    "/{appointment_id}/reschedule",
    response_model=AppointmentResponse,
)
async def reschedule_appointment(
    appointment_id: int,
    reschedule_data: AppointmentReschedule,
    db: AsyncSession = Depends(get_db),
):

    # -----------------------------------------------------
    # Existing appointment find karo
    # -----------------------------------------------------

    query = select(Appointment).where(
        Appointment.id == appointment_id,
    )

    result = await db.execute(query)

    appointment = result.scalar_one_or_none()

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )


    # Cancelled appointment reschedule nahi hogi.
    if appointment.status == "Cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancelled appointment cannot be rescheduled",
        )


    # -----------------------------------------------------
    # Doctor + new date par transaction lock
    # -----------------------------------------------------

    await db.execute(
        text(
            """
            SELECT pg_advisory_xact_lock(
                :doctor_id,
                :appointment_date_key
            )
            """
        ),
        {
            "doctor_id": appointment.doctor_id,
            "appointment_date_key": (
                reschedule_data.appointment_date.toordinal()
            ),
        },
    )


    # -----------------------------------------------------
    # New slot validate karo
    # -----------------------------------------------------

    # IMPORTANT:
    # Validation successful hone se pehle existing
    # appointment ko modify nahi kiya ja raha.
    #
    # Isliye reschedule fail hone par original booking
    # unchanged rahegi.

    await validate_appointment_slot(
        appointment_date=reschedule_data.appointment_date,
        start_time=reschedule_data.start_time,
        duration=reschedule_data.duration,
        doctor_id=appointment.doctor_id,
        db=db,
        exclude_appointment_id=appointment_id,
    )


    # -----------------------------------------------------
    # Validation successful -> appointment update
    # -----------------------------------------------------

    appointment.appointment_date = (
        reschedule_data.appointment_date
    )

    appointment.start_time = (
        reschedule_data.start_time
    )

    appointment.duration = (
        reschedule_data.duration
    )

    appointment.status = "Scheduled"

    await db.commit()
    await db.refresh(appointment)

    return appointment


# =========================================================
# DELETE APPOINTMENT
# =========================================================

@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
):

    query = select(Appointment).where(
        Appointment.id == appointment_id,
    )

    result = await db.execute(query)

    appointment = result.scalar_one_or_none()

    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )


    await db.delete(appointment)

    await db.commit()

    return None