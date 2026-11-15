import json
import re
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.util import Inches, Pt
PDF_PAGE_SIZE = (540, 540)
from reportlab.pdfgen import canvas

from backend.database import get_connection

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "AI_Content_Creator" / "generated_carousels"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def safe_slug(text):
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return slug[:45] or "carousel"


def get_font(size):
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf"
    ]

    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


def generate_slide_content(topic, audience, tone, count):
    headings = [
        topic,
        "Why does this matter?",
        "Understand the basics",
        "Key points to remember",
        "Practical tips",
        "Common mistakes",
        "How to get started",
        "Important takeaways",
        "Your action plan",
        "Keep learning!"
    ]

    descriptions = [
        f"Discover the important ideas about {topic}.",
        f"Learn why {topic} is relevant for {audience}.",
        f"Understand the fundamental concepts of {topic}.",
        f"Focus on the most useful points and ideas.",
        f"Apply what you learn about {topic} in real life.",
        "Avoid common mistakes and build strong foundations.",
        "Start small, practise consistently and improve.",
        "Remember the important lessons from this carousel.",
        "Choose one useful idea and put it into action.",
        "Keep exploring, practising and growing every day."
    ]

    slides = []

    for index in range(count):
        slides.append({
            "slide_number": index + 1,
            "title": headings[index],
            "description": descriptions[index],
            "topic": topic,
            "audience": audience,
            "tone": tone
        })

    return slides


def create_slide_image(slide, output_path):
    image = Image.new("RGB", (1080, 1080), "#211b45")
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        (55, 55, 1025, 1025),
        radius=45,
        fill="#30265f",
        outline="#8c75ff",
        width=5
    )

    draw.text(
        (100, 110),
        "CREATOR AI",
        fill="#c7b9ff",
        font=get_font(35)
    )

    draw.text(
        (100, 225),
        f"SLIDE {slide['slide_number']}",
        fill="#b5a4ff",
        font=get_font(28)
    )

    title = slide["title"]
    words = title.split()
    lines = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()
        if len(test) > 23:
            lines.append(current)
            current = word
        else:
            current = test

    if current:
        lines.append(current)

    y = 340

    for line in lines[:5]:
        draw.text((100, y), line, fill="white", font=get_font(62))
        y += 90

    description = slide["description"]
    draw.text(
        (100, 850),
        description[:65],
        fill="#d7d0f7",
        font=get_font(25)
    )

    image.save(output_path, quality=95)


def create_exports(folder, slides):
    folder.mkdir(parents=True, exist_ok=True)

    # Create PPTX
    presentation = Presentation()
    presentation.slide_width = Inches(10)
    presentation.slide_height = Inches(10)

    for slide_data in slides:
        slide = presentation.slides.add_slide(
            presentation.slide_layouts[6]
        )

        image_path = folder / f"slide_{slide_data['slide_number']}.png"
        slide.shapes.add_picture(
            str(image_path),
            0, 0,
            width=presentation.slide_width,
            height=presentation.slide_height
        )

    presentation.save(folder / "carousel.pptx")

    # Create PDF
    pdf_path = folder / "carousel.pdf"
    pdf = canvas.Canvas(str(pdf_path), pagesize=(540, 540))

    for slide_data in slides:
        image_path = folder / f"slide_{slide_data['slide_number']}.png"
        pdf.drawImage(str(image_path), 0, 0, width=540, height=540)
        pdf.showPage()

    pdf.save()

    # Create ZIP
    zip_path = folder / "carousel_images.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for slide_data in slides:
            image_path = folder / f"slide_{slide_data['slide_number']}.png"
            archive.write(image_path, image_path.name)


def generate_carousel(topic, audience, tone, count):
    slug = safe_slug(topic)

    connection = get_connection()

    cursor = connection.execute("""
        INSERT INTO carousel_projects
        (topic, audience, tone, slide_count, content_json)
        VALUES (?, ?, ?, ?, ?)
    """, (topic, audience, tone, count, "[]"))

    project_id = cursor.lastrowid
    connection.commit()
    connection.close()

    folder = OUTPUT_DIR / f"{project_id}_{slug}"
    folder.mkdir(parents=True, exist_ok=True)

    slides = generate_slide_content(topic, audience, tone, count)

    for slide in slides:
        image_path = folder / f"slide_{slide['slide_number']}.png"
        create_slide_image(slide, image_path)

    create_exports(folder, slides)

    connection = get_connection()
    connection.execute("""
        UPDATE carousel_projects
        SET content_json = ?
        WHERE id = ?
    """, (json.dumps(slides), project_id))

    connection.commit()
    connection.close()

    return {
        "project_id": project_id,
        "topic": topic,
        "slide_count": count,
        "slides": slides,
        "folder": str(folder)
    }


def get_projects():
    connection = get_connection()

    rows = connection.execute("""
        SELECT id, topic, audience, tone, slide_count, created_at
        FROM carousel_projects
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def get_project(project_id):
    connection = get_connection()

    row = connection.execute("""
        SELECT * FROM carousel_projects WHERE id = ?
    """, (project_id,)).fetchone()

    connection.close()

    if not row:
        return None

    result = dict(row)
    result["slides"] = json.loads(result.pop("content_json") or "[]")
    return result


def get_project_folder(project_id):
    matches = list(OUTPUT_DIR.glob(f"{project_id}_*"))
    if not matches:
        return None
    return matches[0]


