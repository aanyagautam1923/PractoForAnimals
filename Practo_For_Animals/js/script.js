const API_BASE = "/api/animals";

let providers = [];
let activeFilter = "all";

const clinicImages = [
    "https://images.unsplash.com/photo-1628009368231-7bb7cfcb0def?w=600",
    "https://images.unsplash.com/photo-1576201836106-db1758fd1c97?w=600",
    "https://images.unsplash.com/photo-1541599540903-216a46ca1dc0?w=600"
];

function escapeHTML(value = "") {
    return String(value).replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function getClinicType(clinic) {
    const name = (clinic.name || "").toLowerCase();

    if (name.includes("hospital")) return "hospital";
    return "vet";
}

async function loadProviders(city = "") {
    const grid = document.getElementById("providerGrid");
    grid.innerHTML = "<p>Loading animal care providers...</p>";

    try {
        const url = new URL(`${API_BASE}/clinics`, window.location.origin);

        if (city.trim()) {
            url.searchParams.set("city", city.trim());
        }

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error("Unable to load clinics.");
        }

        const result = await response.json();
        providers = Array.isArray(result) ? result : (result.clinics || []);
        renderProviders();

    } catch (error) {
        grid.innerHTML = `
            <p>Unable to connect to the server.
            Please start the backend and refresh the page.</p>
        `;
        console.error(error);
    }
}

function renderProviders() {
    const query = document
        .getElementById("providerSearch")
        .value.toLowerCase();

    const location = document
        .getElementById("location")
        .value.toLowerCase();

    const filtered = providers.filter(clinic => {
        const name = (clinic.name || "").toLowerCase();
        const city = (clinic.city || "").toLowerCase();
        const address = (clinic.address || "").toLowerCase();
        const services = Array.isArray(clinic.services)
            ? clinic.services.join(" ").toLowerCase()
            : String(clinic.services || "").toLowerCase();

        const type = getClinicType(clinic);

        const serviceFilters = {
            vet: ["general checkup", "vaccination", "veterinary"],
            hospital: ["surgery", "dental care", "emergency", "hospital"],
            boarding: ["boarding"],
            diagnostics: ["diagnostic", "lab", "test"],
            ngo: ["ngo", "rescue", "shelter"],
            ambulance: ["ambulance", "emergency"]
        };

        const matchesFilter =
            activeFilter === "all" ||
            activeFilter === type ||
            (serviceFilters[activeFilter] || [activeFilter])
                .some(term => services.includes(term));

        const matchesSearch =
            name.includes(query) ||
            city.includes(query) ||
            address.includes(query) ||
            services.includes(query);

        const matchesLocation =
            !location || city.includes(location);

        return matchesFilter && matchesSearch && matchesLocation;
    });

    const grid = document.getElementById("providerGrid");

    grid.innerHTML = filtered.map((clinic, index) => {
        const services = Array.isArray(clinic.services)
            ? clinic.services.join(", ")
            : clinic.services || "General Animal Care";

        const image = clinicImages[index % clinicImages.length];

        return `
            <article class="provider-card">
                <img src="${image}" alt="Animal care clinic" loading="lazy">

                <div class="provider-info">
                    <span class="provider-type">
                        ${escapeHTML(getClinicType(clinic) === "hospital"
                            ? "Animal Hospital"
                            : "Veterinary Clinic")}
                    </span>

                    <h3>${escapeHTML(clinic.name)}</h3>

                    <p>📍 ${escapeHTML(clinic.city)}</p>

                    <p>${escapeHTML(clinic.address || "")}</p>

                    <p>🩺 ${escapeHTML(services)}</p>

                    <p>📞 ${escapeHTML(clinic.phone || "Not available")}</p>

                    <button onclick="showProvider(${Number(clinic.id)})">
                        View Details →
                    </button>

                    <button onclick="openBooking(${Number(clinic.id)})">
                        Book Appointment →
                    </button>
                </div>
            </article>
        `;
    }).join("");

    document.getElementById("emptyMessage").hidden =
        filtered.length !== 0;
}

function filterService(type) {
    activeFilter = type;

    document.querySelectorAll(".filter").forEach(button => {
        button.classList.toggle(
            "active",
            type === "all"
                ? button.textContent.trim() === "All"
                : button.textContent.toLowerCase().includes(type)
        );
    });

    document.getElementById("providerSearch").value = "";

    renderProviders();

    document.getElementById("providers").scrollIntoView({
        behavior: "smooth"
    });
}

async function searchProviders() {
    activeFilter = document.getElementById("service").value;

    await loadProviders(
        document.getElementById("location").value
    );

    document.getElementById("providers").scrollIntoView({
        behavior: "smooth"
    });
}

function showProvider(id) {
    const clinic = providers.find(item => item.id === id);
    if (!clinic) return;

    document.getElementById("modalTitle").textContent = clinic.name;

    document.getElementById("modalDescription").textContent =
        `Location: ${clinic.address || clinic.city}.
        City: ${clinic.city}.
        Phone: ${clinic.phone || "Not available"}.
        Services: ${clinic.services || "General Animal Care"}.`;

    document.getElementById("contactForm").style.display = "none";

    document.getElementById("formMessage").textContent = "";

    document.getElementById("modal").classList.add("show");
}

function openBooking(clinicId) {
    const clinic = providers.find(item => item.id === clinicId);
    if (!clinic) return;

    document.getElementById("modalTitle").textContent =
        "Book an Appointment";

    document.getElementById("modalDescription").textContent =
        `Book an appointment at ${clinic.name}.`;

    const form = document.getElementById("contactForm");

    form.style.display = "block";

    form.innerHTML = `
        <input name="owner_name"
            placeholder="Pet owner's name" required>

        <input name="animal_name"
            placeholder="Pet's name" required>

        <input name="phone"
            type="tel"
            placeholder="Phone number"
            pattern="[0-9+ -]{10,15}"
            required>

        <input name="appointment_date"
            type="datetime-local"
            min="${new Date(Date.now() - new Date().getTimezoneOffset() * 60000)
                .toISOString().slice(0, 16)}"
            required>

        <textarea name="message"
            placeholder="Describe your pet's issue or required service"></textarea>

        <button class="primary-btn" type="submit">
            Confirm Appointment →
        </button>
    `;

    form.onsubmit = async function(event) {
        event.preventDefault();

        const data = Object.fromEntries(new FormData(form).entries());

        data.clinic_id = clinicId;

        const message = document.getElementById("formMessage");
        message.textContent = "Booking your appointment...";

        try {
            const response = await fetch(`${API_BASE}/appointments`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Booking failed.");
            }

            message.textContent =
                "Appointment request submitted successfully! Booking ID: " +
                (result.appointment_id || "Confirmed");

            form.reset();

        } catch (error) {
            message.textContent = error.message;
        }
    };

    document.getElementById("formMessage").textContent = "";
    document.getElementById("modal").classList.add("show");
}


function openModal(type) {
    const isBusiness = type === "business";

    document.getElementById("modalTitle").textContent =
        isBusiness ? "List Your Business" : "Submit a Correction";

    document.getElementById("modalDescription").textContent =
        isBusiness
            ? "Tell us about your animal-care business."
            : "Help us correct information in our directory.";

    const form = document.getElementById("contactForm");
    const message = document.getElementById("formMessage");

    form.style.display = "block";

    form.innerHTML = `
        <input name="name" placeholder="Your name" required minlength="2">
        <input name="email" type="email" placeholder="Email address" required>
        <input name="phone" type="tel" placeholder="Phone number">
        <textarea name="message"
            placeholder="${isBusiness
                ? "Business name, address, city and services..."
                : "Tell us what information needs correction..."}"
            required minlength="5"></textarea>
        <button class="primary-btn" type="submit">
            Submit Request ?
        </button>
    `;

    message.textContent = "";

    form.onsubmit = async function(event) {
        event.preventDefault();

        const submitButton = form.querySelector("button[type='submit']");
        submitButton.disabled = true;
        submitButton.textContent = "Submitting...";

        const data = Object.fromEntries(new FormData(form).entries());

        try {
            const endpoint = isBusiness
                ? `${API_BASE}/business-listings`
                : `${API_BASE}/corrections`;

            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(
                    typeof result.detail === "string"
                        ? result.detail
                        : "Unable to submit request."
                );
            }

            message.textContent =
                `${result.message} Reference ID: ${
                    result.listing_id || result.request_id
                }. Status: ${result.status}.`;

            form.reset();

        } catch (error) {
            message.textContent = error.message;
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = "Submit Request ?";
        }
    };

    document.getElementById("modal").classList.add("show");
}

function closeModal() {
    document.getElementById("modal").classList.remove("show");

    const form = document.getElementById("contactForm");
    form.style.display = "block";
}

document.getElementById("modal").addEventListener("click", event => {
    if (event.target === event.currentTarget) {
        closeModal();
    }
});

document.getElementById("contactForm").addEventListener("submit", event => {
    event.preventDefault();
});

loadProviders();
