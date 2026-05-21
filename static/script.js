let progress = 0;
let interval;

const glow = document.getElementById("cursor-glow");

const templateSelect = document.getElementById("template");
const promptInput = document.getElementById("prompt");

/* =========================
   CURSOR GLOW
========================= */

document.addEventListener("mousemove", (e) => {

    if (!glow) return;

    glow.style.left = `${e.clientX}px`;
    glow.style.top = `${e.clientY}px`;

});

/* =========================
   TEMPLATE PLACEHOLDERS
========================= */

function updatePlaceholder() {

    if (!templateSelect || !promptInput) return;

    if (templateSelect.value === "resume") {

        promptInput.placeholder =
            "Create a clean one-page software engineering resume.";

    } else {

        promptInput.placeholder =
            "Write an article about artificial intelligence.";

    }

}

if (templateSelect) {

    templateSelect.addEventListener(
        "change",
        updatePlaceholder
    );

    updatePlaceholder();

}

/* =========================
   LOADING BAR
========================= */

function startLoading() {

    const container =
        document.getElementById("loader-container");

    const bar =
        document.getElementById("loader-bar");

    if (!container || !bar) return;

    container.classList.add("show");

    progress = 0;

    bar.style.width = "0%";

    interval = setInterval(() => {

        if (progress < 90) {

            progress += Math.random() * 8;

            bar.style.width = `${progress}%`;

        }

    }, 300);

}

function finishLoading(blob) {

    const container =
        document.getElementById("loader-container");

    const bar =
        document.getElementById("loader-bar");

    clearInterval(interval);

    if (bar) {
        bar.style.width = "100%";
    }

    setTimeout(() => {

        if (container) {
            container.classList.remove("show");
        }

        const url =
            window.URL.createObjectURL(blob);

        const a =
            document.createElement("a");

        a.href = url;
        a.download = "document.pdf";

        document.body.appendChild(a);

        a.click();

        a.remove();

        window.URL.revokeObjectURL(url);

    }, 400);

}

function stopLoading() {

    const container =
        document.getElementById("loader-container");

    clearInterval(interval);

    if (container) {
        container.classList.remove("show");
    }

}

/* =========================
   GENERATE PDF
========================= */

async function generatePDF() {

    startLoading();

    try {

        const form =
            document.getElementById("generateForm");

        const formData =
            new FormData(form);

        const res = await fetch(
            "/generate-ui",
            {
                method: "POST",
                body: formData
            }
        );

        const contentType =
            res.headers.get("Content-Type");

        if (!res.ok) {

            let message =
                "Could not generate the document.";

            if (
                contentType &&
                contentType.includes("application/json")
            ) {

                const data =
                    await res.json();

                message =
                    data.error || message;

            } else {

                message =
                    await res.text();

            }

            stopLoading();

            showToast(message);

            return;

        }

        const blob =
            await res.blob();

        finishLoading(blob);

    } catch (error) {

        stopLoading();

        showToast(
            "Something went wrong. Please try again."
        );

        console.error(error);

    }

}

/* =========================
   TOAST
========================= */

function showToast(message) {

    const toast =
        document.getElementById("toast");

    if (!toast) return;

    toast.textContent = message;

    toast.classList.add("show");

    setTimeout(() => {

        toast.classList.remove("show");

    }, 5000);

}