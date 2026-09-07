from fastapi import FastAPI

from app.routers.patient import router as patient_router
from app.routers.doctor import router as doctor_router
from app.routers.appoinment import router as appointment_router
from app.routers.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Hospital API is running"}


app.include_router(patient_router)
app.include_router(doctor_router)
app.include_router(appointment_router)
app.include_router(auth_router)