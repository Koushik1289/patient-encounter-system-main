from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.appointment import KoushikAppointment as Appointment
from src.models.doctor import KoushikDoctor as Doctor


def create_appointment(db: Session, data):
    now = datetime.now(timezone.utc)

    if data.start_time <= now:
        raise HTTPException(status_code=400, detail="Appointment must be in the future")

    doctor = db.query(Doctor).filter(Doctor.id == data.doctor_id).first()
    if not doctor or not doctor.is_active:
        raise HTTPException(status_code=400, detail="Doctor not available")

    start = data.start_time.replace(tzinfo=None)
    end = start + timedelta(minutes=data.duration_minutes)

    existing_appointments = (
        db.query(Appointment).filter(Appointment.doctor_id == data.doctor_id).all()
    )

    for appt in existing_appointments:
        appt_start = appt.start_time
        appt_end = appt_start + timedelta(minutes=appt.duration_minutes)

        if start < appt_end and end > appt_start:
            raise HTTPException(status_code=409, detail="overlap appointment")

    appointment = Appointment(
        patient_id=data.patient_id,
        doctor_id=data.doctor_id,
        start_time=start,
        duration_minutes=data.duration_minutes,
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment
