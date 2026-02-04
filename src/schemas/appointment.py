from datetime import datetime
from pydantic import BaseModel, Field, validator


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    start_time: datetime
    duration_minutes: int = Field(..., ge=15)

    @validator("start_time")
    def require_timezone(cls, u):
        if u.tzinfo is None:
            raise ValueError("Timezone required")
        return u


class AppointmentRead(AppointmentCreate):
    id: int

    class Config:
        orm_mode = True
