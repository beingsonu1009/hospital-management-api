# app/models/patient.py

from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Patient(Base):
    __tablename__ = "patient"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[int]
    gender: Mapped[str]
    disease: Mapped[str]