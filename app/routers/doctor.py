# =========================================================
# app/routers/doctor.py
# Doctor CRUD + Working Hours + JWT Protection
# =========================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.models.doctor import Doctor
from app.models.working_hr import DoctorWorkingHours
from app.schema import (
    DoctorCreate,
    DoctorResponse,
    WorkingHoursCreate,
    WorkingHoursResponse,
)
from app.security import get_current_user


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"],
    # Doctor ke saare endpoints ke liye JWT required hai.
    dependencies=[Depends(get_current_user)],
)


# =========================================================
# GET ALL DOCTORS
# =========================================================

@router.get(
    "",
    response_model=list[DoctorResponse],
)
async def get_doctors(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Doctor).order_by(Doctor.id)
    )

    return result.scalars().all()


# =========================================================
# GET DOCTOR BY ID
# =========================================================

@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
)
async def get_doctor(
    doctor_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Doctor).where(
            Doctor.id == doctor_id
        )
    )

    doctor = result.scalar_one_or_none()

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    return doctor


# =========================================================
# CREATE DOCTOR
# =========================================================

@router.post(
    "",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_doctor(
    doctor_data: DoctorCreate,
    db: AsyncSession = Depends(get_db),
):
    new_doctor = Doctor(
        name=doctor_data.name,
        specialisation=doctor_data.specialisation,
        phone=doctor_data.phone,
        status=doctor_data.status,
    )

    db.add(new_doctor)

    await db.commit()
    await db.refresh(new_doctor)

    return new_doctor


# =========================================================
# UPDATE DOCTOR
# =========================================================

@router.put(
    "/{doctor_id}",
    response_model=DoctorResponse,
)
async def update_doctor(
    doctor_id: int,
    doctor_data: DoctorCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Doctor).where(
            Doctor.id == doctor_id
        )
    )

    doctor = result.scalar_one_or_none()

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    doctor.name = doctor_data.name
    doctor.specialisation = doctor_data.specialisation
    doctor.phone = doctor_data.phone
    doctor.status = doctor_data.status

    await db.commit()
    await db.refresh(doctor)

    return doctor


# =========================================================
# DELETE DOCTOR
# =========================================================

@router.delete(
    "/{doctor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_doctor(
    doctor_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Doctor).where(
            Doctor.id == doctor_id
        )
    )

    doctor = result.scalar_one_or_none()

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    await db.delete(doctor)

    await db.commit()

    return None


# =========================================================
# CREATE WORKING HOURS
# =========================================================

@router.post(
    "/{doctor_id}/working-hours",
    response_model=WorkingHoursResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_working_hours(
    doctor_id: int,
    working_hours_data: WorkingHoursCreate,
    db: AsyncSession = Depends(get_db),
):
    # Pehle verify karo ki doctor exist karta hai.
    doctor_result = await db.execute(
        select(Doctor).where(
            Doctor.id == doctor_id
        )
    )

    doctor = doctor_result.scalar_one_or_none()

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    # Same doctor ke same day ke liye duplicate hours allowed nahi hain.
    existing_result = await db.execute(
        select(DoctorWorkingHours).where(
            DoctorWorkingHours.doctor_id == doctor_id,
            DoctorWorkingHours.day_of_week
            == working_hours_data.day_of_week,
        )
    )

    existing_hours = existing_result.scalar_one_or_none()

    if existing_hours is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Working hours already exist for this day",
        )

    new_working_hours = DoctorWorkingHours(
        doctor_id=doctor_id,
        day_of_week=working_hours_data.day_of_week,
        start_time=working_hours_data.start_time,
        end_time=working_hours_data.end_time,
    )

    db.add(new_working_hours)

    await db.commit()
    await db.refresh(new_working_hours)

    return new_working_hours


# =========================================================
# GET WORKING HOURS
# =========================================================

@router.get(
    "/{doctor_id}/working-hours",
    response_model=list[WorkingHoursResponse],
)
async def get_working_hours(
    doctor_id: int,
    db: AsyncSession = Depends(get_db),
):
    # Doctor exist karta hai ya nahi.
    doctor_result = await db.execute(
        select(Doctor).where(
            Doctor.id == doctor_id
        )
    )

    doctor = doctor_result.scalar_one_or_none()

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    result = await db.execute(
        select(DoctorWorkingHours)
        .where(
            DoctorWorkingHours.doctor_id == doctor_id
        )
        .order_by(
            DoctorWorkingHours.day_of_week
        )
    )

    return result.scalars().all()


# =========================================================
# UPDATE WORKING HOURS
# =========================================================

@router.put(
    "/{doctor_id}/working-hours/{working_hours_id}",
    response_model=WorkingHoursResponse,
)
async def update_working_hours(
    doctor_id: int,
    working_hours_id: int,
    working_hours_data: WorkingHoursCreate,
    db: AsyncSession = Depends(get_db),
):
    # Doctor check.
    doctor_result = await db.execute(
        select(Doctor).where(
            Doctor.id == doctor_id
        )
    )

    doctor = doctor_result.scalar_one_or_none()

    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    # Working-hours record ko doctor ke saath verify karo.
    result = await db.execute(
        select(DoctorWorkingHours).where(
            DoctorWorkingHours.id == working_hours_id,
            DoctorWorkingHours.doctor_id == doctor_id,
        )
    )

    working_hours = result.scalar_one_or_none()

    if working_hours is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Working hours not found",
        )

    # Agar day change ho raha hai to duplicate check karo.
    duplicate_result = await db.execute(
        select(DoctorWorkingHours).where(
            DoctorWorkingHours.doctor_id == doctor_id,
            DoctorWorkingHours.day_of_week
            == working_hours_data.day_of_week,
            DoctorWorkingHours.id != working_hours_id,
        )
    )

    duplicate = duplicate_result.scalar_one_or_none()

    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Working hours already exist for this day",
        )

    working_hours.day_of_week = (
        working_hours_data.day_of_week
    )
    working_hours.start_time = (
        working_hours_data.start_time
    )
    working_hours.end_time = (
        working_hours_data.end_time
    )

    await db.commit()
    await db.refresh(working_hours)

    return working_hours


# =========================================================
# DELETE WORKING HOURS
# =========================================================

@router.delete(
    "/{doctor_id}/working-hours/{working_hours_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_working_hours(
    doctor_id: int,
    working_hours_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DoctorWorkingHours).where(
            DoctorWorkingHours.id == working_hours_id,
            DoctorWorkingHours.doctor_id == doctor_id,
        )
    )

    working_hours = result.scalar_one_or_none()

    if working_hours is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Working hours not found",
        )

    await db.delete(working_hours)

    await db.commit()

    return None