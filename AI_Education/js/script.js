const API_BASE = "/api/education";

const courseSelect = document.getElementById("courseSelect");
const registrationForm = document.getElementById("registrationForm");
const formMessage = document.getElementById("formMessage");

let availableCourses = [];

const courseAliases = {
    "Artificial Intelligence & ML": "Artificial Intelligence",
    "Python Programming": "Python Programming",
    "Data Science & Analytics": "Data Science & Analytics",
    "Web Development": "Web Development",
    "Generative AI & LLMs": "Generative AI",
    "Digital Skills & Tools": "Digital Skills & Tools"
};

async function loadCourses() {
    try {
        const response = await fetch(`${API_BASE}/courses`);

        if (!response.ok) {
            throw new Error("Unable to load courses");
        }

        const data = await response.json();
        availableCourses = data.courses || [];

        console.log("Courses loaded:", availableCourses);

        // Keep existing website options, but connect them with database IDs.
        document.querySelectorAll(".course-card button").forEach(button => {
            button.disabled = false;
        });

    } catch (error) {
        console.error("Course loading error:", error);
    }
}

function registerCourse(course) {
    courseSelect.value = course;
    document.getElementById("register").scrollIntoView({
        behavior: "smooth"
    });

    courseSelect.focus();
}

function findCourseId(selectedCourse) {
    const backendTitle = courseAliases[selectedCourse] || selectedCourse;

    const matchedCourse = availableCourses.find(course =>
        course.title.toLowerCase() === backendTitle.toLowerCase()
    );

    return matchedCourse ? matchedCourse.id : null;
}

registrationForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const submitButton = registrationForm.querySelector(
        'button[type="submit"]'
    );

    const formData = new FormData(registrationForm);

    const selectedCourse = formData.get("course");
    const courseId = findCourseId(selectedCourse);

    const registrationData = {
        student_name: formData.get("name").trim(),
        email: formData.get("email").trim(),
        phone: formData.get("phone").trim(),
        course_id: courseId
    };

    if (!registrationData.student_name ||
        !registrationData.email ||
        !registrationData.phone ||
        !selectedCourse) {

        formMessage.textContent = "Please fill all required fields.";
        return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Submitting...";

    formMessage.textContent = "";

    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(registrationData)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Registration failed.");
        }

        formMessage.textContent =
            "✓ Registration successful! Your enquiry has been saved.";

        formMessage.style.color = "green";

        registrationForm.reset();

        console.log("Registration saved:", result);

    } catch (error) {
        formMessage.textContent =
            "Unable to submit registration. Please try again.";

        formMessage.style.color = "red";

        console.error("Registration error:", error);

    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Submit Enquiry →";
    }
});

async function loadEducationStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const stats = await response.json();

        console.log("Education statistics:", stats);

    } catch (error) {
        console.error("Stats loading error:", error);
    }
}

document.addEventListener("DOMContentLoaded", async function() {
    await loadCourses();
    await loadEducationStats();

    console.log("NextMind AI frontend connected to backend.");
});
