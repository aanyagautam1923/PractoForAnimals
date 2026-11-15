from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Literal

from backend.services.content_service import (
    generate_carousel,
    get_projects,
    get_project,
    get_project_folder
)

router = APIRouter(
    prefix="/api/content",
    tags=["AI Content Creator"]
)


class CarouselRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=300)
    audience: str = "Students"
    tone: str = "Professional"
    slide_count: int = Field(default=5, ge=5, le=10)


@router.post("/generate", status_code=201)
def create_carousel(request: CarouselRequest):
    try:
        result = generate_carousel(
            request.topic,
            request.audience,
            request.tone,
            request.slide_count
        )

        return {
            "message": "Carousel generated successfully",
            **result
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Carousel generation failed: {str(error)}"
        )


@router.get("/projects")
def list_projects():
    return {
        "projects": get_projects()
    }


@router.get("/projects/{project_id}")
def project_details(project_id: int):
    project = get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.get("/projects/{project_id}/download/{file_type}")
def download_project(project_id: int, file_type: Literal["pptx", "pdf", "zip"]):
    folder = get_project_folder(project_id)

    if not folder:
        raise HTTPException(status_code=404, detail="Project files not found")

    files = {
        "pptx": "carousel.pptx",
        "pdf": "carousel.pdf",
        "zip": "carousel_images.zip"
    }

    file_path = folder / files[file_type]

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Export file not found")

    return FileResponse(
        path=file_path,
        filename=file_path.name
    )


@router.get("/projects/{project_id}/slides/{slide_number}")
def get_project_slide(project_id: int, slide_number: int):
    project = get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if slide_number < 1 or slide_number > project["slide_count"]:
        raise HTTPException(status_code=404, detail="Slide not found")

    folder = get_project_folder(project_id)

    if not folder:
        raise HTTPException(status_code=404, detail="Project files not found")

    image_path = folder / f"slide_{slide_number}.png"

    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Slide image not found")

    return FileResponse(image_path, media_type="image/png")
