from datetime import datetime, timedelta, timezone

# ---------------------------------------------------
# CREATE APPOINTMENT
# ---------------------------------------------------

# def test_create_valid_appointment(client):
#     start_time = datetime.now(timezone.utc) + timedelta(hours=1)

#     response = client.post(
#         "/appointments",
#         json={
#             "patient_id": 1,
#             "doctor_id": 1,
#             "start_time": start_time.isoformat(),
#             "duration_minutes": 30,
#         },
#     )

#     assert response.status_code == 201
#     data = response.json()
#     assert data["patient_id"] == 1
#     assert data["doctor_id"] == 1
#     assert data["duration_minutes"] == 30


def test_reject_past_appointment(client):
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


def test_reject_timezone_naive_datetime(client):
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


def test_reject_invalid_duration(client):
    start_time = datetime.now(timezone.utc) + timedelta(hours=2)

    response = client.post(
        "/appointments",
        json={
            "patient_id": 1,
            "doctor_id": 1,
            "start_time": start_time.isoformat(),
            "duration_minutes": 10,  # invalid (<15)
        },
    )

    assert response.status_code == 422


# ---------------------------------------------------
# OVERLAP PREVENTION
# ---------------------------------------------------

# def test_prevent_overlapping_appointments(client):
#     start_time = datetime.now(timezone.utc) + timedelta(hours=3)

#     first = client.post(
#         "/appointments",
#         json={
#             "patient_id": 1,
#             "doctor_id": 1,
#             "start_time": start_time.isoformat(),
#             "duration_minutes": 60,
#         },
#     )
#     assert first.status_code == 201

#     overlapping = client.post(
#         "/appointments",
#         json={
#             "patient_id": 1,
#             "doctor_id": 1,
#             "start_time": (start_time + timedelta(minutes=30)).isoformat(),
#             "duration_minutes": 30,
#         },
#     )
#     assert overlapping.status_code == 409


# def test_allow_non_overlapping_appointments(client):
#     start_time = datetime.now(timezone.utc) + timedelta(hours=5)

#     first = client.post(
#         "/appointments",
#         json={
#             "patient_id": 1,
#             "doctor_id": 1,
#             "start_time": start_time.isoformat(),
#             "duration_minutes": 30,
#         },
#     )
#     assert first.status_code == 201

#     second = client.post(
#         "/appointments",
#         json={
#             "patient_id": 1,
#             "doctor_id": 1,
#             "start_time": (start_time + timedelta(minutes=45)).isoformat(),
#             "duration_minutes": 30,
#         },
#     )
#     assert second.status_code == 201


# ---------------------------------------------------
# LIST APPOINTMENTS BY DATE
# ---------------------------------------------------


def test_list_appointments_by_date(client):
    target_date = (datetime.now(timezone.utc) + timedelta(hours=1)).date()
    date_str = target_date.isoformat()

    response = client.get(f"/appointments?date={date_str}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_appointments_by_date_and_doctor(client):
    target_date = (datetime.now(timezone.utc) + timedelta(hours=1)).date()
    date_str = target_date.isoformat()

    response = client.get(f"/appointments?date={date_str}&doctor_id=1")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
