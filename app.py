
from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader
from io import BytesIO
from markupsafe import escape

app = Flask(__name__)


# Welcome Page
@app.route("/")
def home():
    return render_template("welcome.html")


# BreachBuddy Analyzer Page
@app.route("/analyzer")
def analyzer():
    return render_template("index.html")


# Extract text from PDF or TXT
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")

    if not file or not file.filename:
        return jsonify({"error": "Please select a file."}), 400

    filename = file.filename.lower()

    try:
        if filename.endswith(".txt"):
            text = file.read().decode("utf-8-sig")

        elif filename.endswith(".pdf"):
            pdf = PdfReader(BytesIO(file.read()))

            if pdf.is_encrypted:
                return jsonify({
                    "error": "Password-protected PDFs are not supported."
                }), 400

            text = "\n".join(
                page.extract_text() or "" for page in pdf.pages
            )

        else:
            return jsonify({
                "error": "Only PDF and TXT files are supported."
            }), 400

        if not text.strip():
            return jsonify({
                "error": "No readable text found in the file."
            }), 400

        return jsonify({"text": text})

    except Exception:
        return jsonify({
            "error": "Unable to read this file. Please check the file."
        }), 400


# Simple Explanation
def explain_notice(notice):
    lower = notice.lower()

    explanation = "This notification describes a security incident."

    if "unauthorized access" in lower:
        explanation += (
            " Someone accessed the company's system without permission."
        )

    if "may have been exposed" in lower or "were exposed" in lower:
        explanation += (
            " Some customer information may have been revealed."
        )

    if "email" in lower:
        explanation += " Email addresses may be affected."

    if "phone" in lower:
        explanation += " Phone numbers may be affected."

    if "password" in lower:
        explanation += " Account passwords may be affected."

    if "bank" in lower or "financial" in lower:
        explanation += " Financial information may be affected."

    explanation += " Users should follow the recommended security actions."

    return explanation


# Analyze Breach Notification
@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json(silent=True) or {}
    notice = data.get("notice", "").strip()

    if not notice:
        return jsonify({
            "html": "<p>Please enter a notification.</p>"
        }), 400

    lower_notice = notice.lower()

    categories = {
        "Email Address": [
            "email address", "email addresses", "e-mail"
        ],
        "Phone Number": [
            "phone number", "phone numbers", "mobile number"
        ],
        "Password": [
            "password", "login credentials", "account credentials"
        ],
        "Bank Details": [
            "bank details", "bank account", "banking information"
        ],
        "Personal Information": [
            "personal information", "date of birth",
            "home address", "residential address"
        ],
        "Credit/Debit Card": [
            "credit card", "debit card",
            "card details", "payment card"
        ],
        "Government ID": [
            "passport number", "social security number",
            "government id", "national id"
        ]
    }

    exposed = []

    for category, keywords in categories.items():
        if any(word in lower_notice for word in keywords):
            exposed.append(category)

    # Risk Assessment
    sensitive = [
        "Password",
        "Bank Details",
        "Credit/Debit Card",
        "Government ID"
    ]

    if any(item in exposed for item in sensitive):
        risk = "HIGH"
    elif exposed:
        risk = "MEDIUM"
    else:
        risk = "NOT DETERMINED"

    # Recommended Actions
    actions = []

    if "Password" in exposed:
        actions.extend([
            "Change the affected account password immediately.",
            "Change reused passwords on other accounts.",
            "Enable two-factor authentication (2FA)."
        ])

    if any(item in exposed for item in [
        "Bank Details", "Credit/Debit Card"
    ]):
        actions.extend([
            "Contact your bank using its official contact details.",
            "Monitor account and card transactions."
        ])

    if exposed:
        actions.extend([
            "Review recent account login activity.",
            "Watch for suspicious emails, calls and messages."
        ])
    else:
        actions.append(
            "Contact the company through its official website for clarification."
        )

    explanation = explain_notice(notice)

    exposed_html = "".join(
        f"<li>{escape(item)}</li>" for item in exposed
    ) if exposed else (
        "<li>No supported data category was identified.</li>"
    )

    actions_html = "".join(
        f"<li>{escape(action)}</li>" for action in actions
    )

    result_html = f"""
        <h2>Analysis Results</h2>

        <h3>Simple Explanation</h3>
        <p>{escape(explanation)}</p>

        <h3>Risk Level: {escape(risk)}</h3>

        <h3>Potentially Exposed Data</h3>
        <ul>{exposed_html}</ul>

        <h3>Recommended Actions</h3>
        <ul>{actions_html}</ul>

        <p><strong>Privacy Note:</strong>
        This demo processes the notification in memory and does not
        save it to a database.</p>

        <p><strong>Disclaimer:</strong>
        This is a basic keyword-based analysis. It cannot confirm
        whether information was actually exposed or determine the
        full security risk.</p>
    """

    return jsonify({"html": result_html})


if __name__ == "__main__":
    app.run(debug=True)
