# =========================================================
# app/routers/patient.py
# Patient CRUD + JWT Protection
# =========================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.models.patient import Patient
from app.schema import PatientCreate, PatientResponse
from app.security import get_current_user


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
    # Is router ke saare endpoints ke liye JWT required hai.
    dependencies=[Depends(get_current_user)],
)


# =========================================================
# GET ALL PATIENTS
# =========================================================

@router.get(
    "",
    response_model=list[PatientResponse],
)
async def get_patients(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Patient).order_by(Patient.id)
    )

    return result.scalars().all()


# =========================================================
# GET PATIENT BY ID
# =========================================================

@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
)
async def get_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Patient).where(
            Patient.id == patient_id
        )
    )

    patient = result.scalar_one_or_none()

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return patient


# =========================================================
# CREATE PATIENT
# =========================================================

@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_patient(
    patient_data: PatientCreate,
    db: AsyncSession = Depends(get_db),
):
    new_patient = Patient(
        name=patient_data.name,
        age=patient_data.age,
        gender=patient_data.gender,
        disease=patient_data.disease,
    )

    db.add(new_patient)

    await db.commit()
    await db.refresh(new_patient)

    return new_patient


# =========================================================
# UPDATE PATIENT
# =========================================================

@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
)
async def update_patient(
    patient_id: int,
    patient_data: PatientCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Patient).where(
            Patient.id == patient_id
        )
    )

    patient = result.scalar_one_or_none()

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    patient.name = patient_data.name
    patient.age = patient_data.age
    patient.gender = patient_data.gender
    patient.disease = patient_data.disease

    await db.commit()
    await db.refresh(patient)

    return patient


# =========================================================
# DELETE PATIENT
# =========================================================

@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Patient).where(
            Patient.id == patient_id
        )
    )

    patient = result.scalar_one_or_none()

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    await db.delete(patient)

    await db.commit()

    return None