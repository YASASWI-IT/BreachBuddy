
const notice = document.getElementById("notice");
const result = document.getElementById("result");
const analyzeBtn = document.getElementById("analyzeBtn");
const noticeFile = document.getElementById("noticeFile");
const fileName = document.getElementById("fileName");

// PDF / TXT file upload
noticeFile.addEventListener("change", async () => {
    const file = noticeFile.files[0];

    if (!file) return;

    fileName.textContent = "Selected: " + file.name;
    result.innerHTML = "<p>Reading your file...</p>";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            result.textContent = data.error || "Unable to read file.";
            return;
        }

        notice.value = data.text;
        result.textContent =
            "File uploaded successfully! Click Analyze Notification.";

    } catch (error) {
        result.textContent =
            "File upload failed. Please try again.";
    }
});


// Analyze breach notification
analyzeBtn.addEventListener("click", async () => {
    const notification = notice.value.trim();

    if (!notification) {
        result.textContent =
            "Please paste or upload a breach notification first.";
        return;
    }

    result.textContent = "Analyzing notification...";

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing...";

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                notice: notification
            })
        });

        const data = await response.json();

        if (!response.ok) {
            result.textContent =
                data.error || "Unable to analyze notification.";
            return;
        }

        result.innerHTML = data.html;

    } catch (error) {
        result.textContent =
            "Something went wrong. Please try again.";

    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "🔍 Analyze Notification";
    }
});
