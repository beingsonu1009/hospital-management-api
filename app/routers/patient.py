# APIRouter =It helps us organize routes.
# status =Instead of writing:status_code=201
# HTTPException= Its job is to immediately stop the function and return an HTTP error response.
from fastapi import APIRouter,status,HTTPException,Depends
                                                                #Depends() FastAPI ko batata hai:
                                                                #"Is endpoint ko execute karne se pehle ye dependency provide karo."
from app.schema import PatientCreate ,PatientResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_db
from sqlalchemy import select
from app.models.patient import Patient


router = APIRouter(                                             # router=just a variable name it store an apiRouter object/# APIRouter= create a router
    prefix="/patients",         
    tags=["Patients"]                                            # tags=["Patients"]This is only for Swagger UI.
    
)

#endpoint of get

@router.get(
    "",
    response_model=list[PatientResponse],
    status_code=status.HTTP_200_OK
)
async def get_all_patients(
    db: AsyncSession = Depends(get_db)
):
    statement= select(Patient)
    result= await db.execute(statement)
    patients = result.scalars().all()
    
    return patients

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    statement = select(Patient).where(Patient.id == patient_id)

    result = await db.execute(statement)

    patient = result.scalar_one_or_none()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient

@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
    status_code=status.HTTP_200_OK
)


# creating endpoint of post
@router.post(                                                        #This is called a decorator.
    "",
    response_model=PatientResponse,                                 #"Whatever I return, convert and validate it according to PatientResponse."
    status_code=status.HTTP_201_CREATED                             #f everything succeeds, send HTTP 201 Created

)

async def create_patient(
    patient: PatientCreate,
    db: AsyncSession = Depends(get_db)                               #Aur database session FastAPI se lenge:
):
    new_patient = Patient(
    name=patient.name,
    age=patient.age,
    gender=patient.gender,
    disease=patient.disease
)

    db.add(new_patient)                                              #This is not synchronus 
    await db.commit()                                                   #it is synchronus
    await db.refresh(new_patient)                                    #refresh() SQLAlchemy object ko database ki latest values se update karta hai.                      
    return new_patient                                                 #Api response



# def create_patient(patient:PatientCreate):                    #This parameter will contain the request body.
#                                                                # Body part
#     patient_data = patient.model_dump()                       #model dump will convert it in dif type so we can easily edit it
# # Bussiness logic
#     patient_data["id"]=len(patients)+1                        #Its job is to count items.           
#     patients.append(patient_data)                              # Now we're going to save the patient.
#     return patient_data 





# Now we'll write the update logic
    
async def update_patient(
    patient_id: int,
    patient: PatientCreate,
    db: AsyncSession = Depends(get_db)
):
    # patient find
    statement = select(Patient).where(Patient.id == patient_id)
    result = await db.execute(statement)
    existing_patient = result.scalar_one_or_none()

# not found
    if existing_patient is None:
        raise HTTPException(
        status_code=404,
        detail="Patient not found"
    )

# update
    existing_patient.name = patient.name
    existing_patient.age = patient.age
    existing_patient.gender = patient.gender
    existing_patient.disease = patient.disease

# save
    await db.commit()

# refresh
    await db.refresh(existing_patient)
    return existing_patient

#Delete endpoint 
@router.delete(
     "/{patient_id}",
    #  response_model=PatientResponse,
     status_code=status.HTTP_204_NO_CONTENT
)

async def delete_patient(
    patient_id: int,
    db: AsyncSession = Depends(get_db)
):
    statement = select(Patient).where(Patient.id == patient_id)

    result = await db.execute(statement)

    existing_patient = result.scalar_one_or_none()

    if existing_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient Not Found"
        )
    await db.delete(existing_patient)

    await db.commit()
    return {"message": "Patient deleted successfully"}