from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta

from src.database import Base, engine, get_db
from src.models.appointment import KoushikAppointment as Appointment

from src.schemas.patient import PatientCreate, PatientRead
from src.schemas.doctor import DoctorCreate, DoctorRead
from src.schemas.appointment import AppointmentCreate, AppointmentRead

from src.services.patient_service import create_patient, get_patient
from src.services.doctor_service import create_doctor, get_doctor, deactivate_doctor
from src.services.appointment_service import create_appointment

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MEMS")


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/health")
def health():
    return {"status": "UP"}


@app.post("/patients", response_model=PatientRead, status_code=201)
def create_patient_api(payload: PatientCreate, db: Session = Depends(get_db)):
    return create_patient(db, payload)


@app.get("/patients/{patient_id}", response_model=PatientRead)
def get_patient_api(patient_id: int, db: Session = Depends(get_db)):
    return get_patient(db, patient_id)


@app.post("/doctors", response_model=DoctorRead, status_code=201)
def create_doctor_api(payload: DoctorCreate, db: Session = Depends(get_db)):
    return create_doctor(db, payload)


@app.get("/doctors/{doctor_id}", response_model=DoctorRead)
def get_doctor_api(doctor_id: int, db: Session = Depends(get_db)):
    return get_doctor(db, doctor_id)


@app.patch("/doctors/{doctor_id}/deactivate", response_model=DoctorRead)
def deactivate_doctor_api(doctor_id: int, db: Session = Depends(get_db)):
    return deactivate_doctor(db, doctor_id)


@app.post("/appointments", response_model=AppointmentRead, status_code=201)
def create_appointment_api(payload: AppointmentCreate, db: Session = Depends(get_db)):
    return create_appointment(db, payload)


@app.get("/appointments", response_model=list[AppointmentRead])
def list_appointments(
    date_: date = Query(..., alias="date"),
    doctor_id: int | None = None,
    db: Session = Depends(get_db),
):
    start_dt = datetime.combine(date_, datetime.min.time())
    end_dt = start_dt + timedelta(days=1)

    query = db.query(Appointment).filter(
        Appointment.start_time >= start_dt,
        Appointment.start_time < end_dt,
    )

    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)

    return query.all()
