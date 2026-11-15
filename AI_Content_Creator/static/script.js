(function () {
    "use strict";

    const Creator = {
        notify(message, type = "success") {
            let toast = document.getElementById("static-toast");

            if (!toast) {
                toast = document.createElement("div");
                toast.id = "static-toast";
                toast.setAttribute("role", "status");
                document.body.appendChild(toast);
            }

            toast.textContent = message;
            toast.className = "static-toast visible " + type;

            clearTimeout(this.timer);
            this.timer = setTimeout(() => {
                toast.classList.remove("visible");
            }, 3000);
        },

        async copyText(value) {
            try {
                await navigator.clipboard.writeText(value);
                this.notify("Copied successfully!");
            } catch {
                this.notify("Clipboard access unavailable.", "error");
            }
        },

        downloadBlob(blob, filename) {
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");

            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            link.remove();

            setTimeout(() => URL.revokeObjectURL(url), 1000);
        },

        escapeHTML(value) {
            return String(value ?? "").replace(/[&<>"']/g, char => ({
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            })[char]);
        }
    };

    window.PractoContentCreator = Creator;

    document.addEventListener("click", event => {
        const button = event.target.closest("[data-copy]");

        if (button) {
            Creator.copyText(button.dataset.copy);
        }
    });

    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll("[data-current-year]").forEach(element => {
            element.textContent = new Date().getFullYear();
        });
    });
})();
