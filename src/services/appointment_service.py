from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.appointment import KoushikAppointment as KoushikAppointment
from src.models.doctor import KoushikDoctor as KoushikDoctor


def create_appointment(db: Session, data):
    now = datetime.now(timezone.utc)

    if data.start_time <= now:
        raise HTTPException(status_code=400, detail="Appointment must be in the future")

    doctor = db.query(KoushikDoctor).filter(KoushikDoctor.id == data.doctor_id).first()
    if not doctor or not doctor.is_active:
        raise HTTPException(status_code=400, detail="Doctor not available")

    start = data.start_time
    end = start + timedelta(minutes=data.duration_minutes)

    overlapping = (
        db.query(KoushikAppointment)
        .filter(
            KoushikAppointment.doctor_id == data.doctor_id,
            KoushikAppointment.start_time < end,
            (
                KoushikAppointment.start_time
                + timedelta(minutes=KoushikAppointment.duration_minutes)
            )
            > start,
        )
        .first()
    )

    if overlapping:
        raise HTTPException(status_code=409, detail="Overlapping appointment")

    appt = KoushikAppointment(**data.dict())
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt
