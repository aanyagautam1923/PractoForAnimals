const API_BASE = "/api/content";

let currentProjectId = null;

function showCreatorMessage(message, type = "success") {
    if (typeof showToast === "function") {
        showToast(message);
    } else {
        alert(message);
    }
}

function createElement(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
}

function renderSlides(project) {
    const previewGrid = document.getElementById("previewGrid");
    if (!previewGrid) return;

    previewGrid.replaceChildren();
    currentProjectId = project.id;

    const count = Number(project.slide_count || 0);

    for (let i = 1; i <= count; i++) {
        const card = createElement("article", "slide-card");
        const visual = createElement("div", "slide-visual");

        const image = document.createElement("img");
        image.src = `${API_BASE}/projects/${project.id}/slides/${i}`;
        image.alt = `Carousel slide ${i}`;
        image.loading = "lazy";
        image.style.width = "100%";
        image.style.height = "100%";
        image.style.objectFit = "contain";

        visual.appendChild(image);

        const info = createElement("div", "slide-info");
        info.appendChild(createElement("h3", "", `Slide ${i}`));

        card.append(visual, info);
        previewGrid.appendChild(card);
    }

    addDownloadButtons(project.id, previewGrid);
}

function addDownloadButtons(projectId, container) {
    const downloads = createElement("div", "project-downloads");
    downloads.style.display = "flex";
    downloads.style.flexWrap = "wrap";
    downloads.style.gap = "10px";
    downloads.style.margin = "20px 0";

    [
        ["Download PPTX", "pptx"],
        ["Download PDF", "pdf"],
        ["Download Images ZIP", "zip"]
    ].forEach(([label, type]) => {
        const link = createElement("a", "btn", label);
        link.href = `${API_BASE}/projects/${projectId}/download/${type}`;
        link.download = "";
        link.style.textDecoration = "none";
        downloads.appendChild(link);
    });

    container.appendChild(downloads);
}

async function generateCarousel() {
    const topic = document.getElementById("topic")?.value.trim();
    const audience = document.getElementById("audience")?.value;
    const tone = document.getElementById("tone")?.value;
    const slideCount = Number(document.getElementById("slides")?.value || 5);
    const button = document.getElementById("generateBtn");

    if (!topic) {
        showCreatorMessage("Please enter a carousel topic.");
        return;
    }

    if (button) {
        button.disabled = true;
        button.textContent = "Generating...";
    }

    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                topic,
                audience,
                tone,
                slide_count: slideCount
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Could not generate carousel.");
        }

        const project = data.project || data;
        renderSlides(project);
        await loadProjects();

        showCreatorMessage("Carousel generated successfully!");
    } catch (error) {
        console.error("Carousel generation error:", error);
        showCreatorMessage(error.message || "Something went wrong.");
    } finally {
        if (button) {
            button.disabled = false;
            button.textContent = "Generate Carousel";
        }
    }
}

async function loadProjects() {
    try {
        const response = await fetch(`${API_BASE}/projects`);

        if (!response.ok) {
            throw new Error("Unable to load projects.");
        }

        const data = await response.json();
        const projects = Array.isArray(data) ? data : (data.projects || []);

        const countElement = document.getElementById("projectCount");
        const slideElement = document.getElementById("slideCount");

        if (countElement) countElement.textContent = projects.length;

        if (slideElement) {
            const totalSlides = projects.reduce(
                (total, project) => total + Number(project.slide_count || 0),
                0
            );
            slideElement.textContent = totalSlides;
        }

        renderProjectHistory(projects);
    } catch (error) {
        console.error("Project loading error:", error);
    }
}

function renderProjectHistory(projects) {
    let history = document.getElementById("projectHistory");

    if (!history) {
        history = createElement("section", "project-history");
        history.id = "projectHistory";

        const projectsSection = document.getElementById("projects");
        if (projectsSection) {
            projectsSection.appendChild(history);
        } else {
            document.body.appendChild(history);
        }
    }

    history.replaceChildren();
    history.appendChild(createElement("h2", "", "My Generated Projects"));

    if (!projects.length) {
        history.appendChild(createElement("p", "", "No projects generated yet."));
        return;
    }

    projects.forEach(project => {
        const card = createElement("article", "slide-card");
        const title = createElement("h3", "", project.topic || `Project ${project.id}`);
        const details = createElement(
            "p",
            "",
            `${project.slide_count || 0} slides • ${project.audience || "General audience"}`
        );

        const actions = createElement("div", "project-actions");

        const viewButton = createElement("button", "btn", "View Slides");
        viewButton.type = "button";
        viewButton.addEventListener("click", () => openProject(project.id));

        actions.appendChild(viewButton);

        card.append(title, details, actions);
        addDownloadButtons(project.id, card);
        history.appendChild(card);
    });
}

async function openProject(projectId) {
    try {
        const response = await fetch(`${API_BASE}/projects/${projectId}`);

        if (!response.ok) {
            throw new Error("Project details could not be loaded.");
        }

        const data = await response.json();
        const project = data.project || data;

        renderSlides(project);

        document.getElementById("creator")?.scrollIntoView({
            behavior: "smooth"
        });
    } catch (error) {
        console.error(error);
        showCreatorMessage(error.message);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadProjects();
});
