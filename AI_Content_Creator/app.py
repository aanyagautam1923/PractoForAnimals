import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pathlib import Path
from datetime import datetime
import io
import zipfile
import json
import re
import textwrap

BASE = Path(__file__).parent
OUTPUT = BASE / "generated_carousels"
OUTPUT.mkdir(exist_ok=True)

st.set_page_config(
    page_title="CreatorAI | Content Studio",
    page_icon="✨",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

html,body,[class*="css"] {
    font-family:'DM Sans',sans-serif;
}
.stApp {
    background:#f7f7fc;
}
section[data-testid="stSidebar"] {
    background:#17152f;
}
section[data-testid="stSidebar"] * {
    color:white;
}
.main-title {
    font-size:34px;
    font-weight:800;
    color:#22203e;
}
.subtitle {
    color:#85849a;
    font-size:14px;
}
.metric-box {
    background:white;
    padding:22px;
    border-radius:14px;
    border:1px solid #ecebf4;
}
.metric-number {
    font-size:27px;
    font-weight:800;
    color:#7054e8;
}
.metric-label {
    color:#88869b;
    font-size:12px;
}
.panel {
    background:white;
    padding:24px;
    border-radius:14px;
    border:1px solid #ecebf4;
    margin-bottom:15px;
}
.slide-preview {
    background:linear-gradient(145deg,#29234f,#7658ed);
    color:white;
    padding:30px;
    border-radius:12px;
    min-height:240px;
}
.stButton>button {
    border-radius:8px;
    font-weight:700;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# CONTENT GENERATION ENGINE
# ==========================================

def generate_content(topic, audience, tone, count):

    topic = topic.strip()

    templates = [
        (
            f"What is {topic}?",
            f"Let's understand {topic} in simple terms.",
            f"Start with the fundamentals and build your understanding step by step."
        ),
        (
            f"Why does {topic} matter?",
            f"{topic} can play an important role in today's world.",
            "Understanding its purpose helps you make better decisions."
        ),
        (
            f"Key concepts of {topic}",
            "Break the topic into smaller ideas.",
            "Focus on definitions, practical examples and important concepts."
        ),
        (
            f"Common mistakes in {topic}",
            "Avoid learning without understanding.",
            "Practice consistently and verify what you learn."
        ),
        (
            f"How to get started with {topic}",
            "Start small and keep learning.",
            "Choose one concept, practise it and gradually increase the difficulty."
        ),
        (
            f"Practical applications of {topic}",
            "Theory becomes valuable when you apply it.",
            "Explore real-world examples and build small projects."
        ),
        (
            f"Tips to master {topic}",
            "Consistency matters more than speed.",
            "Create a learning routine and track your progress."
        ),
        (
            f"Your next step",
            f"Start exploring {topic} today.",
            "Save this carousel and share it with someone who wants to learn."
        )
    ]

    slides = []

    for i in range(count):
        title, subtitle, body = templates[i % len(templates)]

        slides.append({
            "title": title,
            "subtitle": subtitle,
            "body": body,
            "number": i + 1
        })

    return {
        "topic": topic,
        "audience": audience,
        "tone": tone,
        "slides": slides
    }


# ==========================================
# IMAGE GENERATION
# ==========================================

def create_slide_image(slide, topic, index):

    width, height = 1080, 1080

    backgrounds = [
        (38, 32, 79),
        (84, 62, 157),
        (40, 69, 110),
        (100, 54, 116),
        (35, 91, 89)
    ]

    img = Image.new("RGB", (width, height), backgrounds[index % 5])
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arial.ttf", 76)
        body_font = ImageFont.truetype("arial.ttf", 38)
        small_font = ImageFont.truetype("arial.ttf", 25)
    except OSError:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    draw.ellipse((760, -170, 1250, 320), outline=(150, 125, 230), width=5)
    draw.ellipse((-150, 820, 260, 1230), outline=(150, 125, 230), width=5)

    draw.text((75, 75), "CREATOR AI  /  CONTENT STUDIO",
              fill=(205, 194, 255), font=small_font)

    draw.line((75, 135, 1000, 135), fill=(130, 115, 200), width=2)

    title = slide["title"]

    y = 270

    for line in textwrap.wrap(title, width=19):
        draw.text((75, y), line, fill="white", font=title_font)
        y += 100

    y += 35

    for line in textwrap.wrap(slide["subtitle"], width=38):
        draw.text((75, y), line, fill=(220, 215, 255), font=body_font)
        y += 55

    y += 45

    for line in textwrap.wrap(slide["body"], width=48):
        draw.text((75, y), line, fill=(235, 232, 250), font=small_font)
        y += 42

    draw.line((75, 965, 1000, 965), fill=(130, 115, 200), width=2)

    draw.text((75, 985), topic[:40], fill="white", font=small_font)
    draw.text((900, 985), f"{index + 1:02d}/08",
              fill="white", font=small_font)

    return img


# ==========================================
# POWERPOINT EXPORT
# ==========================================

def create_pptx(data, images):

    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(10)

    for img in images:

        slide = prs.slides.add_slide(prs.slide_layouts[6])

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        slide.shapes.add_picture(
            buffer, 0, 0,
            width=prs.slide_width,
            height=prs.slide_height
        )

    output = io.BytesIO()
    prs.save(output)
    output.seek(0)

    return output.getvalue()


# ==========================================
# PDF EXPORT
# ==========================================

def create_pdf(data):

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    for slide in data["slides"]:

        pdf.setFillColorRGB(0.14, 0.12, 0.30)
        pdf.rect(0, 0, width, height, fill=1)

        pdf.setFillColorRGB(0.85, 0.80, 1)
        pdf.setFont("Helvetica", 11)
        pdf.drawString(45, height - 55, "CREATOR AI | CONTENT STUDIO")

        pdf.setFillColorRGB(1, 1, 1)
        pdf.setFont("Helvetica-Bold", 28)

        y = height - 180

        for line in textwrap.wrap(slide["title"], 25):
            pdf.drawString(45, y, line)
            y -= 42

        pdf.setFont("Helvetica", 17)
        pdf.setFillColorRGB(0.85, 0.83, 1)

        for line in textwrap.wrap(slide["subtitle"], 42):
            pdf.drawString(45, y - 20, line)
            y -= 27

        pdf.setFillColorRGB(1, 1, 1)
        pdf.setFont("Helvetica", 12)

        for line in textwrap.wrap(slide["body"], 65):
            pdf.drawString(45, y - 70, line)
            y -= 20

        pdf.showPage()

    pdf.save()
    buffer.seek(0)

    return buffer.getvalue()


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("# ✨ CreatorAI")
    st.caption("AI CONTENT STUDIO")

    st.divider()

    page = st.radio(
        "WORKSPACE",
        [
            "Dashboard",
            "Create Carousel",
            "My Projects",
            "About"
        ]
    )

    st.divider()

    st.markdown("### Your Workspace")
    st.caption("Content creation made simple.")
    st.caption("Version 1.0")


# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.markdown('<div class="main-title">Welcome to CreatorAI ✨</div>',
                unsafe_allow_html=True)

    st.markdown(
        '<div class="subtitle">Your creative workspace for social media content.</div>',
        unsafe_allow_html=True
    )

    st.write("")

    projects = st.session_state.get("projects", [])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f'<div class="metric-box"><div class="metric-number">{len(projects)}</div><div class="metric-label">Total Projects</div></div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f'<div class="metric-box"><div class="metric-number">{sum(len(p["slides"]) for p in projects)}</div><div class="metric-label">Slides Created</div></div>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            '<div class="metric-box"><div class="metric-number">3</div><div class="metric-label">Export Formats / Tools</div></div>',
            unsafe_allow_html=True
        )

    st.write("")
    st.subheader("Start Creating")

    if st.button("＋ Create New Carousel", type="primary"):
        st.session_state["page_action"] = "Create Carousel"
        st.rerun()

    st.info(
        "Enter a topic, choose your audience and tone, "
        "and generate a carousel ready for editing and export."
    )

    st.subheader("Recent Projects")

    if projects:
        for project in reversed(projects[-5:]):
            st.write(
                f"📁 **{project['topic']}** — "
                f"{len(project['slides'])} slides"
            )
    else:
        st.caption("No projects created yet.")


# ==========================================
# CREATE CAROUSEL
# ==========================================

elif page == "Create Carousel" or st.session_state.get("page_action") == "Create Carousel":

    st.session_state["page_action"] = None

    st.markdown('<div class="main-title">Create Your Carousel ✨</div>',
                unsafe_allow_html=True)

    st.markdown(
        '<div class="subtitle">Turn your ideas into beautiful social media slides.</div>',
        unsafe_allow_html=True
    )

    with st.form("generator_form"):

        topic = st.text_input(
            "What topic do you want to create content about?",
            placeholder="Example: Artificial Intelligence"
        )

        c1, c2 = st.columns(2)

        with c1:
            audience = st.selectbox(
                "Target Audience",
                [
                    "Students",
                    "Professionals",
                    "Beginners",
                    "Entrepreneurs",
                    "General Audience"
                ]
            )

        with c2:
            tone = st.selectbox(
                "Content Tone",
                [
                    "Professional",
                    "Friendly",
                    "Educational",
                    "Creative",
                    "Motivational"
                ]
            )

        slide_count = st.slider(
            "Number of Slides",
            min_value=4,
            max_value=8,
            value=8
        )

        generate = st.form_submit_button(
            "✨ Generate Carousel",
            type="primary",
            use_container_width=True
        )

    if generate:

        if not topic.strip():
            st.error("Please enter a topic first.")

        else:

            with st.spinner("Creating your carousel..."):

                data = generate_content(
                    topic,
                    audience,
                    tone,
                    slide_count
                )

                images = [
                    create_slide_image(slide, topic, i)
                    for i, slide in enumerate(data["slides"])
                ]

                data["created_at"] = datetime.now().strftime(
                    "%d %b %Y %H:%M"
                )

                st.session_state["current_project"] = data
                st.session_state["current_images"] = images

                projects = st.session_state.get("projects", [])
                projects.append(data)
                st.session_state["projects"] = projects

                OUTPUT.mkdir(exist_ok=True)

                safe_name = re.sub(
                    r"[^a-zA-Z0-9_-]", "_", topic
                )[:40]

                project_dir = OUTPUT / safe_name
                project_dir.mkdir(exist_ok=True)

                for i, img in enumerate(images):
                    img.save(project_dir / f"slide_{i+1}.png")

                with open(
                    project_dir / "content.json",
                    "w",
                    encoding="utf-8"
                ) as f:
                    json.dump(data, f, indent=4)

            st.success("Your carousel has been generated!")

    data = st.session_state.get("current_project")
    images = st.session_state.get("current_images")

    if data and images:

        st.divider()
        st.subheader(f"Preview: {data['topic']}")

        for i, slide in enumerate(data["slides"]):

            with st.expander(
                f"Slide {i+1}: {slide['title']}",
                expanded=(i == 0)
            ):

                left, right = st.columns([1, 1])

                with left:
                    st.image(images[i], use_container_width=True)

                with right:
                    st.text_input(
                        "Headline",
                        value=slide["title"],
                        key=f"title_{i}"
                    )

                    st.text_input(
                        "Subtitle",
                        value=slide["subtitle"],
                        key=f"subtitle_{i}"
                    )

                    st.text_area(
                        "Description",
                        value=slide["body"],
                        key=f"body_{i}"
                    )

                    if st.button("Save Slide Changes", key=f"save_{i}"):

                        slide["title"] = st.session_state[f"title_{i}"]
                        slide["subtitle"] = st.session_state[f"subtitle_{i}"]
                        slide["body"] = st.session_state[f"body_{i}"]

                        images[i] = create_slide_image(
                            slide, data["topic"], i
                        )

                        st.session_state["current_project"] = data
                        st.session_state["current_images"] = images

                        st.success("Slide updated.")
                        st.rerun()

        st.divider()
        st.subheader("Download Your Work")

        a, b, c = st.columns(3)

        with a:
            pptx = create_pptx(data, images)

            st.download_button(
                "📊 Download PowerPoint",
                pptx,
                file_name="creatorai_carousel.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )

        with b:
            pdf = create_pdf(data)

            st.download_button(
                "📄 Download PDF",
                pdf,
                file_name="creatorai_carousel.pdf",
                mime="application/pdf"
            )

        with c:

            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(
                zip_buffer, "w", zipfile.ZIP_DEFLATED
            ) as archive:

                for i, img in enumerate(images):
                    image_buffer = io.BytesIO()
                    img.save(image_buffer, format="PNG")

                    archive.writestr(
                        f"slide_{i+1}.png",
                        image_buffer.getvalue()
                    )

            st.download_button(
                "🖼 Download Images",
                zip_buffer.getvalue(),
                file_name="carousel_images.zip",
                mime="application/zip"
            )


# ==========================================
# MY PROJECTS
# ==========================================

elif page == "My Projects":

    st.markdown('<div class="main-title">My Projects 📁</div>',
                unsafe_allow_html=True)

    projects = st.session_state.get("projects", [])

    if not projects:

        st.info("You have not created any projects yet.")

    else:

        for i, project in enumerate(reversed(projects)):

            with st.expander(project["topic"]):

                st.write("Audience:", project["audience"])
                st.write("Tone:", project["tone"])
                st.write("Slides:", len(project["slides"]))
                st.write("Created:", project.get("created_at", "Unknown"))

                if st.button("Open Project", key=f"open_{i}"):

                    st.session_state["current_project"] = project

                    st.success(
                        "Project loaded. Open Create Carousel to preview."
                    )


# ==========================================
# ABOUT
# ==========================================

elif page == "About":

    st.markdown("# About CreatorAI")

    st.write("""
    CreatorAI is a social media content creation dashboard.

    ### Core Technologies

    - Python
    - Streamlit
    - Pillow
    - Python-PPTX
    - ReportLab

    ### Features

    - Topic-based carousel content generation
    - Automatic slide design
    - Editable slide content
    - PowerPoint export
    - PDF export
    - Image ZIP export

    ### Generation Engine

    This version uses a local template-based content engine.
    It does not call an external LLM API.
    """)

st.markdown("---")
st.caption("CreatorAI Content Studio | Educational Product Development Project")
