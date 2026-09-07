from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.models.appointment import Appointment
from app.schema import AppointmentCreate, AppointmentResponse


# Appointment ke saare API endpoints isi router ke andar honge
router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)



# CREATE APPOINTMENT


@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_appointment(
    appointment: AppointmentCreate,
    db: AsyncSession = Depends(get_db)
):
    # Request body se data lekar SQLAlchemy ORM object bana rahe hain
    new_appointment = Appointment(
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date,
        reason=appointment.reason,
        status=appointment.status
    )

    # Appointment ko database session mein add karna
    db.add(new_appointment)

    # Transaction ko database mein save karna
    await db.commit()

    # Database-generated values, jaise id, object mein reload karna
    await db.refresh(new_appointment)

    # Created appointment return karna
    return new_appointment



# READ ALL APPOINTMENTS


@router.get(
    "/",
    response_model=list[AppointmentResponse]
)
async def get_appointments(
    db: AsyncSession = Depends(get_db)
):
    # SELECT query create karna
    query = select(Appointment)

    # Query asynchronously execute karna
    result = await db.execute(query)

    # Appointment ORM objects nikalna
    appointments = result.scalars().all()

    # Saare appointments return karna
    return appointments



# READ ONE APPOINTMENT


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
async def get_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Given ID ke according appointment search karna
    query = select(Appointment).where(
        Appointment.id == appointment_id
    )

    # Query execute karna
    result = await db.execute(query)

    # Ek appointment retrieve karna
    appointment = result.scalar_one_or_none()

    # Appointment nahi mila
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    # Appointment mil gaya
    return appointment



# UPDATE APPOINTMENT


@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
async def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentCreate,
    db: AsyncSession = Depends(get_db)
):
    # Pehle existing appointment find karna
    query = select(Appointment).where(
        Appointment.id == appointment_id
    )

    result = await db.execute(query)

    appointment = result.scalar_one_or_none()

    # Appointment nahi mila
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    # Existing appointment ki values update karna
    appointment.patient_id = appointment_data.patient_id
    appointment.doctor_id = appointment_data.doctor_id
    appointment.appointment_date = appointment_data.appointment_date
    appointment.reason = appointment_data.reason
    appointment.status = appointment_data.status

    # Changes database mein save karna
    await db.commit()

    # Updated object refresh karna
    await db.refresh(appointment)

    # Updated appointment return karna
    return appointment



# DELETE APPOINTMENT


@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Delete karne se pehle appointment find karna
    query = select(Appointment).where(
        Appointment.id == appointment_id
    )

    result = await db.execute(query)

    appointment = result.scalar_one_or_none()

    # Appointment nahi mila
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    # Appointment ko delete ke liye mark karna
    await db.delete(appointment)

    # Delete transaction commit karna
    await db.commit()

    # 204 No Content mein response body nahi hoti
    return None