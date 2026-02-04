from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_create_valid_appointment():
    start_time = datetime.now(timezone.utc) + timedelta(hours=1)

    response = client.post(
        "/appointments",
        json={
            "patient_id": 1,
            "doctor_id": 1,
            "start_time": start_time.isoformat(),
            "duration_minutes": 30,
        },
    )

    assert response.status_code == 201
    assert response.json()["duration_minutes"] == 30


def test_reject_past_appointment():
    past_time = datetime.now(timezone.utc) - timedelta(hours=1)

    response = client.post(
        "/appointments",
        json={
            "patient_id": 1,
            "doctor_id": 1,
            "start_time": past_time.isoformat(),
            "duration_minutes": 30,
        },
    )

    assert response.status_code == 400


def test_reject_timezone_naive_datetime():
    naive_time = (datetime.utcnow() + timedelta(hours=2)).isoformat()

    response = client.post(
        "/appointments",
        json={
            "patient_id": 1,
            "doctor_id": 1,
            "start_time": naive_time,
            "duration_minutes": 30,
        },
    )

    assert response.status_code == 422


def test_reject_invalid_duration():
    start_time = datetime.now(timezone.utc) + timedelta(hours=2)

    response = client.post(
        "/appointments",
        json={
            "patient_id": 1,
            "doctor_id": 1,
            "start_time": start_time.isoformat(),
            "duration_minutes": 5,
        },
    )

    assert response.status_code == 422


def test_prevent_overlapping_appointments():
    start_time = datetime.now(timezone.utc) + timedelta(hours=3)

    r1 = client.post(
        "/appointments",
        json={
            "patient_id": 1,
            "doctor_id": 1,
            "start_time": start_time.isoformat(),
            "duration_minutes": 60,
        },
    )
    assert r1.status_code == 201

    r2 = client.post(
        "/appointments",
        json={
            "patient_id": 1,
            "doctor_id": 1,
            "start_time": (start_time + timedelta(minutes=30)).isoformat(),
            "duration_minutes": 30,
        },
    )

    assert r2.status_code == 409


def test_list_appointments_by_date():
    date_str = (datetime.now(timezone.utc) + timedelta(hours=3)).date().isoformat()

    response = client.get(f"/appointments?date={date_str}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
