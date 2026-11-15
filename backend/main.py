from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from backend.database import init_db
from backend.routers.animals import router as animals_router, seed_clinics
from backend.routers.education import router as education_router, seed_courses
from backend.routers.content_creator import router as content_router

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="PractoForAnimals Multi Product Platform",
    description="Backend APIs for Practo for Animals, AI Education and AI Content Creator",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

# API Routers
app.include_router(animals_router)
app.include_router(education_router)
app.include_router(content_router)


@app.on_event("startup")
def startup():
    init_db()
    seed_clinics()
    seed_courses()


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PractoForAnimals Platform</title>
        <style>
            * { box-sizing: border-box; }
            body {
                margin: 0;
                min-height: 100vh;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg,#101827,#172c46);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 30px;
            }
            .container { max-width: 1050px; width: 100%; text-align: center; }
            h1 { font-size: 38px; margin-bottom: 10px; }
            .subtitle { color: #b8c7d9; margin-bottom: 40px; }
            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit,minmax(250px,1fr));
                gap: 22px;
            }
            .card {
                background: #ffffff12;
                border: 1px solid #ffffff25;
                padding: 30px;
                border-radius: 18px;
                text-align: left;
            }
            .icon { font-size: 42px; }
            h2 { margin: 18px 0 10px; }
            p { color: #c4d0df; line-height: 1.6; min-height: 50px; }
            a {
                display: inline-block;
                margin-top: 18px;
                background: #38bdf8;
                color: #071827;
                text-decoration: none;
                font-weight: bold;
                padding: 12px 20px;
                border-radius: 9px;
            }
            a:hover { background: #7dd3fc; }
            .api { margin-top: 35px; }
            .api a { background: #22c55e; }
        </style>
    </head>
    <body>
        <main class="container">
            <h1>PractoForAnimals Platform</h1>
            <p class="subtitle">One platform. Three intelligent products.</p>

            <div class="cards">
                <section class="card">
                    <div class="icon">🐾</div>
                    <h2>Practo for Animals</h2>
                    <p>Find veterinary clinics and manage animal healthcare appointments.</p>
                    <a href="/practo/">Open Website</a>
                </section>

                <section class="card">
                    <div class="icon">🎓</div>
                    <h2>AI Education</h2>
                    <p>Explore courses, discover learning opportunities and register.</p>
                    <a href="/education/">Open Website</a>
                </section>

                <section class="card">
                    <div class="icon">✨</div>
                    <h2>AI Content Creator</h2>
                    <p>Create carousel content and export your projects.</p>
                    <a href="/creator/">Open Website</a>
                </section>
            </div>
        </main>
    </body>
    </html>
    """


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "database": "SQLite",
        "backend": "FastAPI",
        "products_connected": 3
    }


# Serve all three frontend websites
app.mount(
    "/practo",
    StaticFiles(directory=str(BASE_DIR / "Practo_For_Animals"), html=True),
    name="practo"
)

app.mount(
    "/education",
    StaticFiles(directory=str(BASE_DIR / "AI_Education"), html=True),
    name="education"
)

app.mount(
    "/creator",
    StaticFiles(directory=str(BASE_DIR / "AI_Content_Creator"), html=True),
    name="creator"
)
