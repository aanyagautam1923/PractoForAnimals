from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

from backend.database import get_connection

router = APIRouter(prefix="/api/animals", tags=["Practo for Animals"])


class ClinicCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    city: str = Field(min_length=2, max_length=100)
    address: Optional[str] = None
    phone: Optional[str] = None
    services: Optional[str] = None


class AppointmentCreate(BaseModel):
    owner_name: str = Field(min_length=2, max_length=100)
    animal_name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=10, max_length=15)
    clinic_id: Optional[int] = None
    appointment_date: Optional[str] = None
    message: Optional[str] = None


def seed_clinics():
    connection = get_connection()

    count = connection.execute(
        "SELECT COUNT(*) FROM clinics"
    ).fetchone()[0]

    if count == 0:
        demo_clinics = [
            (
                "Happy Paws Veterinary Clinic",
                "Kanpur",
                "Civil Lines, Kanpur",
                "9876543210",
                "General Checkup, Vaccination"
            ),
            (
                "Pet Care Animal Hospital",
                "Kanpur",
                "Swaroop Nagar, Kanpur",
                "9876543211",
                "Surgery, Dental Care, Emergency"
            ),
            (
                "Healthy Tails Pet Clinic",
                "Lucknow",
                "Gomti Nagar, Lucknow",
                "9876543212",
                "Vaccination, Grooming, General Checkup"
            )
        ]

        connection.executemany("""
            INSERT INTO clinics (name, city, address, phone, services)
            VALUES (?, ?, ?, ?, ?)
        """, demo_clinics)

        connection.commit()

    connection.close()


@router.get("/clinics")
def get_clinics(
    city: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None)
):
    connection = get_connection()

    sql = "SELECT * FROM clinics WHERE 1=1"
    params = []

    if city:
        sql += " AND city LIKE ?"
        params.append(f"%{city}%")

    if search:
        sql += " AND (name LIKE ? OR services LIKE ? OR address LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    sql += " ORDER BY name"

    rows = connection.execute(sql, params).fetchall()
    connection.close()

    return {
        "count": len(rows),
        "clinics": [dict(row) for row in rows]
    }


@router.get("/clinics/{clinic_id}")
def get_clinic(clinic_id: int):
    connection = get_connection()

    row = connection.execute(
        "SELECT * FROM clinics WHERE id = ?",
        (clinic_id,)
    ).fetchone()

    connection.close()

    if not row:
        raise HTTPException(status_code=404, detail="Clinic not found")

    return dict(row)


@router.post("/clinics", status_code=201)
def add_clinic(clinic: ClinicCreate):
    connection = get_connection()

    cursor = connection.execute("""
        INSERT INTO clinics (name, city, address, phone, services)
        VALUES (?, ?, ?, ?, ?)
    """, (
        clinic.name,
        clinic.city,
        clinic.address,
        clinic.phone,
        clinic.services
    ))

    connection.commit()
    clinic_id = cursor.lastrowid
    connection.close()

    return {
        "message": "Clinic added successfully",
        "clinic_id": clinic_id
    }


@router.post("/appointments", status_code=201)
def book_appointment(appointment: AppointmentCreate):
    connection = get_connection()

    if appointment.clinic_id is not None:
        clinic = connection.execute(
            "SELECT id FROM clinics WHERE id = ?",
            (appointment.clinic_id,)
        ).fetchone()

        if not clinic:
            connection.close()
            raise HTTPException(status_code=404, detail="Clinic not found")

    cursor = connection.execute("""
        INSERT INTO appointments
        (owner_name, animal_name, phone, clinic_id, appointment_date, message)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        appointment.owner_name,
        appointment.animal_name,
        appointment.phone,
        appointment.clinic_id,
        appointment.appointment_date,
        appointment.message
    ))

    connection.commit()
    appointment_id = cursor.lastrowid
    connection.close()

    return {
        "message": "Appointment request submitted successfully",
        "appointment_id": appointment_id,
        "status": "Pending"
    }


@router.get("/appointments")
def get_appointments():
    connection = get_connection()

    rows = connection.execute("""
        SELECT appointments.*, clinics.name AS clinic_name
        FROM appointments
        LEFT JOIN clinics ON appointments.clinic_id = clinics.id
        ORDER BY appointments.id DESC
    """).fetchall()

    connection.close()

    return {
        "count": len(rows),
        "appointments": [dict(row) for row in rows]
    }


class BusinessListingCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: str = Field(min_length=5, max_length=150)
    phone: Optional[str] = None
    message: str = Field(min_length=5, max_length=2000)


class CorrectionRequestCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: str = Field(min_length=5, max_length=150)
    phone: Optional[str] = None
    message: str = Field(min_length=5, max_length=2000)


@router.post("/business-listings", status_code=201)
def submit_business_listing(data: BusinessListingCreate):
    connection = get_connection()
    cursor = connection.execute("""
        INSERT INTO business_listings (name, email, phone, message)
        VALUES (?, ?, ?, ?)
    """, (data.name, data.email, data.phone, data.message))
    connection.commit()
    listing_id = cursor.lastrowid
    connection.close()

    return {
        "message": "Business listing submitted successfully.",
        "listing_id": listing_id,
        "status": "Pending"
    }


@router.get("/business-listings")
def get_business_listings():
    connection = get_connection()
    rows = connection.execute(
        "SELECT * FROM business_listings ORDER BY id DESC"
    ).fetchall()
    connection.close()

    return {
        "count": len(rows),
        "listings": [dict(row) for row in rows]
    }


@router.post("/corrections", status_code=201)
def submit_correction(data: CorrectionRequestCreate):
    connection = get_connection()
    cursor = connection.execute("""
        INSERT INTO correction_requests (name, email, phone, message)
        VALUES (?, ?, ?, ?)
    """, (data.name, data.email, data.phone, data.message))
    connection.commit()
    request_id = cursor.lastrowid
    connection.close()

    return {
        "message": "Correction request submitted successfully.",
        "request_id": request_id,
        "status": "Pending"
    }


@router.get("/corrections")
def get_correction_requests():
    connection = get_connection()
    rows = connection.execute(
        "SELECT * FROM correction_requests ORDER BY id DESC"
    ).fetchall()
    connection.close()

    return {
        "count": len(rows),
        "requests": [dict(row) for row in rows]
    }
