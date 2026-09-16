# =========================================================
# app/main.py
# Main FastAPI application
# =========================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth
from app.routers import patient
from app.routers import doctor
from app.routers import appoinment


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Hospital Management API",
    version="0.1.0",
)


# =========================================================
# CORS
# =========================================================

# Frontend se backend API ko access karne ke liye
# allowed origins define kar rahe hain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROUTERS
# =========================================================

# Authentication public rahegi:
# register + login
app.include_router(auth.router)

# Patient APIs JWT protected hain.
app.include_router(patient.router)

# Doctor + Working Hours APIs JWT protected hain.
app.include_router(doctor.router)

# Appointment APIs JWT protected hain.
app.include_router(appoinment.router)


# =========================================================
# HOME / HEALTH CHECK
# =========================================================

@app.get("/")
async def home():
    return {
        "message": "Hospital Management API is running"
    }