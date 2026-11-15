from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

from backend.database import get_connection

router = APIRouter(prefix="/api/education", tags=["AI Education"])


class CourseCreate(BaseModel):
    title: str = Field(min_length=2)
    description: str = ""
    duration: str = ""
    level: str = "Beginner"


class RegistrationCreate(BaseModel):
    student_name: str = Field(min_length=2)
    email: str
    phone: Optional[str] = None
    course_id: Optional[int] = None



def seed_courses():
    connection = get_connection()

    courses = [
        (
            "Artificial Intelligence",
            "Learn AI fundamentals and real-world applications.",
            "12 Weeks",
            "Beginner"
        ),
        (
            "Machine Learning",
            "Understand ML algorithms and predictive models.",
            "10 Weeks",
            "Intermediate"
        ),
        (
            "Python Programming",
            "Learn Python programming from basics to advanced.",
            "8 Weeks",
            "Beginner"
        ),
        (
            "Deep Learning",
            "Explore neural networks and deep learning.",
            "12 Weeks",
            "Advanced"
        ),
        (
            "Generative AI",
            "Learn LLMs, prompt engineering and AI applications.",
            "8 Weeks",
            "Intermediate"
        ),
        (
            "Data Science & Analytics",
            "Learn data analysis, visualization and insights.",
            "10 Weeks",
            "Intermediate"
        ),
        (
            "Web Development",
            "Create modern websites using HTML, CSS and JavaScript.",
            "8 Weeks",
            "Beginner"
        ),
        (
            "Digital Skills & Tools",
            "Develop essential digital productivity and technology skills.",
            "6 Weeks",
            "Beginner"
        )
    ]

    for title, description, duration, level in courses:
        exists = connection.execute(
            "SELECT id FROM courses WHERE title = ?",
            (title,)
        ).fetchone()

        if not exists:
            connection.execute("""
                INSERT INTO courses (title, description, duration, level)
                VALUES (?, ?, ?, ?)
            """, (title, description, duration, level))

    connection.commit()
    connection.close()


@router.get("/courses")
def get_courses(search: Optional[str] = None):
    connection = get_connection()

    sql = "SELECT * FROM courses"
    params = []

    if search:
        sql += " WHERE title LIKE ? OR description LIKE ?"
        params = [f"%{search}%", f"%{search}%"]

    sql += " ORDER BY id"

    courses = connection.execute(sql, params).fetchall()
    connection.close()

    return {
        "count": len(courses),
        "courses": [dict(course) for course in courses]
    }


@router.get("/courses/{course_id}")
def get_course(course_id: int):
    connection = get_connection()

    course = connection.execute(
        "SELECT * FROM courses WHERE id = ?",
        (course_id,)
    ).fetchone()

    connection.close()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    return dict(course)


@router.post("/courses", status_code=201)
def add_course(course: CourseCreate):
    connection = get_connection()

    cursor = connection.execute("""
        INSERT INTO courses (title, description, duration, level)
        VALUES (?, ?, ?, ?)
    """, (
        course.title,
        course.description,
        course.duration,
        course.level
    ))

    connection.commit()
    course_id = cursor.lastrowid
    connection.close()

    return {
        "message": "Course created successfully",
        "course_id": course_id
    }


@router.post("/register", status_code=201)
def register_student(student: RegistrationCreate):
    connection = get_connection()

    if student.course_id is not None:
        course = connection.execute(
            "SELECT id FROM courses WHERE id = ?",
            (student.course_id,)
        ).fetchone()

        if not course:
            connection.close()
            raise HTTPException(status_code=404, detail="Course not found")

    cursor = connection.execute("""
        INSERT INTO registrations
        (student_name, email, phone, course_id)
        VALUES (?, ?, ?, ?)
    """, (
        student.student_name,
        student.email,
        student.phone,
        student.course_id
    ))

    connection.commit()
    registration_id = cursor.lastrowid
    connection.close()

    return {
        "message": "Registration successful",
        "registration_id": registration_id
    }


@router.get("/registrations")
def get_registrations():
    connection = get_connection()

    records = connection.execute("""
        SELECT registrations.*, courses.title AS course_title
        FROM registrations
        LEFT JOIN courses ON registrations.course_id = courses.id
        ORDER BY registrations.id DESC
    """).fetchall()

    connection.close()

    return {
        "count": len(records),
        "registrations": [dict(record) for record in records]
    }


@router.get("/stats")
def education_stats():
    connection = get_connection()

    courses = connection.execute(
        "SELECT COUNT(*) FROM courses"
    ).fetchone()[0]

    students = connection.execute(
        "SELECT COUNT(*) FROM registrations"
    ).fetchone()[0]

    connection.close()

    return {
        "total_courses": courses,
        "total_registrations": students
    }
