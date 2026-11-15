@'
# Practo For Animals – Integrated AI Platform

## 1. Introduction

Practo For Animals is an integrated web application containing three major modules:

1. Practo For Animals
2. AI Education
3. AI Content Creator

The platform combines animal healthcare discovery, online educational course registration and social media content creation.

## 2. Objectives

- Help pet owners discover veterinary clinics.
- Allow users to submit appointment requests.
- Accept business listing and correction requests.
- Provide educational courses.
- Allow students to register for courses.
- Generate social media carousel content.
- Export content into PPTX, PDF and ZIP formats.
- Store application data using SQLite.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API development |
| SQLite | Database |
| HTML5 | Frontend structure |
| CSS3 | Frontend styling |
| JavaScript | Frontend functionality |
| Pillow | Image generation |
| python-pptx | PowerPoint generation |
| ReportLab | PDF generation |
| Uvicorn | Application server |
| Pytest | Testing |

## 4. Practo For Animals

This module provides animal healthcare discovery features.

### Features
- Veterinary clinic listing.
- Clinic search.
- Clinic details.
- Appointment requests.
- Business listing requests.
- Correction requests.

### API Endpoints

| Method | Endpoint |
|---|---|
| GET | `/api/animals/clinics` |
| GET | `/api/animals/clinics/{clinic_id}` |
| POST | `/api/animals/clinics` |
| POST | `/api/animals/appointments` |
| GET | `/api/animals/appointments` |
| POST | `/api/animals/business-listings` |
| GET | `/api/animals/business-listings` |
| POST | `/api/animals/corrections` |
| GET | `/api/animals/corrections` |

## 5. AI Education

This module provides educational courses and registration functionality.

### Features
- Course listing.
- Course search.
- Course information.
- Student registration.
- Registration records.
- Education statistics.

### API Endpoints

| Method | Endpoint |
|---|---|
| GET | `/api/education/courses` |
| GET | `/api/education/courses/{course_id}` |
| POST | `/api/education/courses` |
| POST | `/api/education/register` |
| GET | `/api/education/registrations` |
| GET | `/api/education/stats` |

## 6. AI Content Creator

This module generates carousel content for social media.

### Features
- Topic-based content generation.
- Audience selection.
- Tone selection.
- Multiple slide generation.
- Slide image creation.
- Carousel preview.
- Project history.
- PowerPoint export.
- PDF export.
- ZIP image export.

### API Endpoints

| Method | Endpoint |
|---|---|
| POST | `/api/content/generate` |
| GET | `/api/content/projects` |
| GET | `/api/content/projects/{project_id}` |
| GET | `/api/content/projects/{project_id}/slides/{slide_number}` |
| GET | `/api/content/projects/{project_id}/download/{file_type}` |

**Note:** The current content generator uses programmed templates. It should not be represented as a connected generative AI model unless an actual model integration is added.

## 7. Database

The project uses SQLite.

Database location:

`backend/practo_platform.db`

The database stores:
- Clinics
- Appointments
- Business listings
- Correction requests
- Courses
- Student registrations
- Carousel projects

## 8. Application Routes

| Route | Description |
|---|---|
| `/` | Main platform |
| `/practo/` | Practo For Animals |
| `/education/` | AI Education |
| `/creator/` | AI Content Creator |
| `/api/health` | Backend health check |
| `/docs` | FastAPI API documentation |

## 9. Installation

Use Python 3.12.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt