# HealthPredict — AI Blood Test Analyser

A Flask + Bootstrap health prediction application that manages patient blood test records and uses **Claude AI** to auto-generate health assessment remarks.

---

## Features

- ✅ Full **CRUD** (Create, Read, Update, Delete) for patient records
- 🤖 **AI-powered health remarks** via Claude (Anthropic API) on every save/update
- 🔒 **Data validation** — email format, past-only DOB, numeric blood values
- 💾 **SQLite persistent storage** via Flask-SQLAlchemy
- 📊 **Dashboard stats** — total patients, high glucose, high cholesterol counts
- 🔍 **Live search** — filter patients by name or email
- 📱 **Responsive** — Bootstrap 5 mobile-friendly layout

---

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
```bash
# Linux / macOS
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows CMD
set ANTHROPIC_API_KEY=your-api-key-here
# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Run the app
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

---

## Project Structure

```
health_app/
├── app.py               # Flask backend — routes, models, AI integration
├── requirements.txt     # Python dependencies
├── README.md
└── templates/
    └── index.html       # Single-page Bootstrap UI with modals
```

---

## Blood Test Reference Ranges

| Metric       | Normal Range                        | Unit  |
|-------------|--------------------------------------|-------|
| Glucose     | 70 – 99 (fasting)                   | mg/dL |
| Haemoglobin | 12.0–15.5 (F) / 13.5–17.5 (M)      | g/dL  |
| Cholesterol | < 200 (desirable)                   | mg/dL |

Colour coding in the table:
- 🟢 **Green** = Normal range
- 🟡 **Amber** = Borderline / pre-risk
- 🔴 **Red** = High / abnormal

---

## AI Integration

When a patient record is saved or updated, the app sends the blood values to Claude with a structured medical prompt. Claude returns a 2–3 sentence health assessment that is stored in the **Remarks** field and displayed in the patient record view.

---

## Notes

- The AI remarks are for **educational / demonstration purposes only** and are not medical advice.
- The SQLite database (`health_records.db`) is auto-created in the project root on first run.
