"""
Database table creation script.

Is file ko manually run karke PostgreSQL database mein
SQLAlchemy models ke according tables create kiye ja sakte hain.
"""

import asyncio

from app.db.base import Base
from app.db.session import engine


# ---------------------------------------------------------
# Model Imports
# ---------------------------------------------------------
# IMPORTANT:
# In models ko import karna zaroori hai.
#
# Import hone ke baad SQLAlchemy in models ko
# Base.metadata mein register karta hai.
#
# Phir create_all() ko pata hota hai ki kaun-kaun
# se tables create karne hain.

from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.user import User
from app.models.working_hr import DoctorWorkingHours


# ---------------------------------------------------------
# Create Database Tables
# ---------------------------------------------------------

async def create_tables():
    """
    Database mein required tables create karta hai.

    Existing tables ko unnecessarily delete nahi karta.
    """

    async with engine.begin() as conn:

        # Async connection ke andar SQLAlchemy ke
        # synchronous metadata operation ko run kar rahe hain.
        await conn.run_sync(
            Base.metadata.create_all
        )

    print("Tables created successfully!")


# ---------------------------------------------------------
# Script Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(create_tables())