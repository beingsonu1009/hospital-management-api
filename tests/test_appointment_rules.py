import os
from datetime import date, time, timedelta
from operator import eq, ne

import pytest
from fastapi import HTTPException
from sqlalchemy.sql.elements import BinaryExpression

# Imports of the application database module require a configured URL, but
# these tests replace the database session and never open a connection.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://test:test@127.0.0.1:5432/test_db",
)

from app.models.appointment import Appointment
from app.models.working_hr import DoctorWorkingHours
from app.routers import appoinment
from app.schema import AppointmentReschedule


class FakeResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        if isinstance(self.value, list):
            return self.value[0] if self.value else None
        return self.value

    def scalars(self):
        return self

    def all(self):
        return self.value


class FakeAsyncSession:
    """Small async-session substitute for exercising the route rules."""

    def __init__(self, *, working_hours, appointments=()):
        self.working_hours = working_hours
        self.appointments = list(appointments)

    async def execute(self, statement, parameters=None):
        # The routes issue this PostgreSQL-only statement to serialize
        # bookings. These behavior tests exercise validation after the lock.
        if not hasattr(statement, "column_descriptions"):
            return FakeResult(None)

        model = statement.column_descriptions[0]["entity"]
        if model is DoctorWorkingHours:
            matches = self.working_hours
        elif model is Appointment:
            matches = self.appointments
        else:
            raise AssertionError(f"Unexpected query model: {model}")

        for criterion in statement._where_criteria:
            if not isinstance(criterion, BinaryExpression):
                continue
            key = criterion.left.key
            value = criterion.right.value
            if criterion.operator is eq:
                matches = [row for row in matches if getattr(row, key) == value]
            elif criterion.operator is ne:
                matches = [row for row in matches if getattr(row, key) != value]

        if model is DoctorWorkingHours:
            return FakeResult(matches[0] if matches else None)
        return FakeResult(matches)

    def add(self, item):
        self.appointments.append(item)

    async def commit(self):
        pass

    async def refresh(self, item):
        pass


@pytest.fixture
def booking_date():
    return date.today() + timedelta(days=1)


def make_working_hours(booking_date, start=time(9), end=time(17)):
    return DoctorWorkingHours(
        id=1,
        doctor_id=1,
        day_of_week=booking_date.weekday() + 1,
        start_time=start,
        end_time=end,
    )


def make_appointment(booking_date, start, duration, *, appointment_id=1, status="Scheduled"):
    return Appointment(
        id=appointment_id,
        patient_id=1,
        doctor_id=1,
        appointment_date=booking_date,
        start_time=start,
        duration=duration,
        reason="Consultation",
        status=status,
    )


def make_db(booking_date, appointments=(), *, start=time(9), end=time(17)):
    return FakeAsyncSession(
        working_hours=[make_working_hours(booking_date, start, end)],
        appointments=appointments,
    )


@pytest.mark.asyncio
async def test_overlapping_booking_is_rejected(booking_date):
    db = make_db(booking_date, [make_appointment(booking_date, time(10), 30)])

    with pytest.raises(HTTPException) as error:
        await appoinment.validate_appointment_slot(
            booking_date, time(10, 15), 30, 1, db
        )

    assert error.value.status_code == 409


@pytest.mark.asyncio
async def test_back_to_back_bookings_are_allowed(booking_date):
    db = make_db(booking_date, [make_appointment(booking_date, time(10), 30)])

    await appoinment.validate_appointment_slot(
        booking_date, time(10, 30), 30, 1, db
    )


@pytest.mark.asyncio
async def test_booking_outside_working_hours_is_rejected(booking_date):
    db = make_db(booking_date)

    with pytest.raises(HTTPException) as error:
        await appoinment.validate_appointment_slot(
            booking_date, time(16, 45), 30, 1, db
        )

    assert error.value.status_code == 400
    assert "working hours" in error.value.detail


@pytest.mark.asyncio
async def test_cancelling_appointment_frees_its_slot(booking_date):
    appointment = make_appointment(booking_date, time(10), 30)
    db = make_db(booking_date, [appointment])

    with pytest.raises(HTTPException):
        await appoinment.validate_appointment_slot(
            booking_date, time(10), 30, 1, db
        )

    await appoinment.cancel_appointment(appointment.id, db)
    await appoinment.validate_appointment_slot(
        booking_date, time(10), 30, 1, db
    )

    assert appointment.status == "Cancelled"


@pytest.mark.asyncio
async def test_failed_reschedule_keeps_original_booking(booking_date):
    original = make_appointment(booking_date, time(10), 30, appointment_id=1)
    blocker = make_appointment(booking_date, time(12), 30, appointment_id=2)
    db = make_db(booking_date, [original, blocker])
    before = (original.appointment_date, original.start_time, original.duration)

    with pytest.raises(HTTPException) as error:
        await appoinment.reschedule_appointment(
            original.id,
            AppointmentReschedule(
                appointment_date=booking_date,
                start_time=time(12, 15),
                duration=30,
            ),
            db,
        )

    assert error.value.status_code == 409
    assert (original.appointment_date, original.start_time, original.duration) == before


@pytest.mark.asyncio
async def test_appointment_crossing_midnight_is_rejected(booking_date):
    db = make_db(booking_date, start=time(0), end=time(23, 59))

    with pytest.raises(HTTPException) as error:
        await appoinment.validate_appointment_slot(
            booking_date, time(23, 45), 30, 1, db
        )

    assert error.value.status_code == 400
    assert error.value.detail == "Appointment cannot cross midnight"
