from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.dependencies import get_db
from app.models.doctor import Doctor
from app.schema import DoctorCreate, DoctorResponse
from fastapi import APIRouter, Depends, status, HTTPException


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)

@router.post(
    "",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_doctor(
    doctor: DoctorCreate,
    db: AsyncSession = Depends(get_db)
):
    
    new_doctor = Doctor(
    name=doctor.name,
    specialisation=doctor.specialisation,
    phone=doctor.phone,
    status=doctor.status
)
    db.add(new_doctor)
    await db.commit()
    await db.refresh(new_doctor)
    return new_doctor

@router.get(
    "",
    response_model=list[DoctorResponse]
)
async def get_all_doctors(
    db: AsyncSession = Depends(get_db)
):
        statement = select(Doctor)

        result = await db.execute(statement)

        doctors = result.scalars().all()

        return doctors

@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse
)
async def get_doctor(
    doctor_id: int,
    db: AsyncSession = Depends(get_db)
):
    statement = select(Doctor).where(Doctor.id == doctor_id)

    result = await db.execute(statement)

    existing_doctor = result.scalar_one_or_none()

    if existing_doctor is None:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Doctor Not Found"
    )
        return existing_doctor


@router.put(
    "/{doctor_id}",                  # URL: /doctors/2
    response_model=DoctorResponse    # Response ko DoctorResponse ke format me validate karega
)
async def update_doctor(
    doctor_id: int,                  # URL se doctor ki ID milegi
    doctor: DoctorCreate,             # Request body se updated doctor data milega
    db: AsyncSession = Depends(get_db) # FastAPI Dependency Injection se DB session milega
):

    # Database me given ID wala doctor search karne ke liye query
    statement = select(Doctor).where(Doctor.id == doctor_id)

    # Query ko database me execute karna
    result = await db.execute(statement)

    # Database result se ek Doctor object nikalna
    # Doctor nahi mila to None milega
    existing_doctor = result.scalar_one_or_none()

    # Agar doctor database me exist nahi karta
    if existing_doctor is None:

        # Client ko 404 Not Found response dena
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor Not Found"
        )

    # Existing doctor ki values ko new values se update karna
    existing_doctor.name = doctor.name
    existing_doctor.specialisation = doctor.specialisation
    existing_doctor.phone = doctor.phone
    existing_doctor.status = doctor.status

    # Changes ko PostgreSQL database me permanently save karna
    await db.commit()

    # Database se latest values lekar object ko refresh karna
    await db.refresh(existing_doctor)

    # Updated doctor ko response me return karna
    return existing_doctor

@router.delete(
    "/{doctor_id}",                       # URL: /doctors/2
    status_code=status.HTTP_204_NO_CONTENT # Successful deletion → 204
)
async def delete_doctor(
    doctor_id: int,                       # URL se doctor ki ID
    db: AsyncSession = Depends(get_db)    # FastAPI DB session provide karega
):

    # Given ID wala doctor database me search karna
    statement = select(Doctor).where(Doctor.id == doctor_id)

    # Query execute karna
    result = await db.execute(statement)

    # Result se Doctor object nikalna
    # Doctor nahi mila → None
    existing_doctor = result.scalar_one_or_none()

    # Doctor exist nahi karta
    if existing_doctor is None:

        # 404 response dena
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor Not Found"
        )

    # Doctor object ko database session se delete ke liye mark karna
    await db.delete(existing_doctor)

    # Delete operation ko PostgreSQL me permanently save karna
    await db.commit()

    # 204 No Content me normally response body nahi hoti
    return
