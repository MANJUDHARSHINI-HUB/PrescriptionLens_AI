# 💊 PrescriptionLens AI — OCR Prescription Chatbot

PrescriptionLens AI is a portfolio project that turns a photo of a prescription into
organized, structured information and lets you ask questions about it through an
AI chatbot. It combines **OpenCV**, **EasyOCR**, an **LLM**, **FastAPI**, and
**Streamlit** into a simple, end-to-end application.

> ⚠️ **Medical Safety Disclaimer**
> This application extracts and organizes information from a prescription and
> provides general educational information. It does **not** diagnose conditions
> or prescribe/change medication. **Always verify medication instructions with
> your doctor or pharmacist.**

---

## ✨ Features

- 📷 Upload a prescription image directly in the browser
- 🖼️ OpenCV preprocessing (resize, grayscale, denoise, adaptive threshold) to improve OCR accuracy
- 🔍 Text extraction using **EasyOCR**, with a manual correction step before analysis
- 💊 LLM-based structured medicine extraction (name, strength, dosage, frequency, timing, food relation, duration) — **only what's explicitly written; missing fields are `null`, never invented**
- ⏰ A timing checklist built strictly from timing explicitly present in the prescription (session-persisted checkboxes)
- 🤖 An AI chatbot that answers questions grounded in the uploaded prescription, and clearly labels general medical info as educational, replying **"I cannot determine that from the uploaded prescription."** when it doesn't know
- 💡 General wellness tips section (no diagnosis, no treatment changes)
- 🧩 Clean separation between a FastAPI backend and a Streamlit frontend
- 🐳 Docker Compose setup for one-command startup
- ✅ Pytest test suite for the API

---

## 🏗️ Architecture

```
┌─────────────────┐      HTTP       ┌──────────────────────┐
│  Streamlit UI    │ ───────────────▶│   FastAPI Backend     │
│  (frontend/app.py)│◀─────────────── │   (backend/main.py)   │
└─────────────────┘                 └──────────┬────────────┘
                                                │
                     ┌──────────────────────────┼──────────────────────────┐
                     ▼                          ▼                          ▼
            ocr_service.py           extraction_service.py           chat_service.py
         (OpenCV + EasyOCR)              (LLM → JSON)                (LLM → grounded Q&A)
```

**Flow:** Image → OpenCV preprocessing → EasyOCR text → user verification →
LLM structured extraction → medicine cards + timing checklist → chatbot Q&A
grounded in the same prescription text and structured data.

---

## 🛠️ Technology Stack

| Layer          | Technology                     |
|----------------|---------------------------------|
| Frontend       | Streamlit                      |
| Backend/API    | FastAPI, Pydantic, Uvicorn      |
| Image Processing | OpenCV (opencv-python-headless) |
| OCR            | EasyOCR                        |
| AI/Chatbot     | LLM API (Anthropic Messages API by default) |
| Config         | python-dotenv (`.env`)         |
| Containerization | Docker, Docker Compose        |
| Testing        | Pytest, FastAPI TestClient      |

---

## 📁 Project Structure

```
PrescriptionLens_AI/
│
├── frontend/
│   └── app.py                  # Streamlit UI
│
├── backend/
│   ├── main.py                 # FastAPI app & routes
│   ├── ocr_service.py          # OpenCV + EasyOCR pipeline
│   ├── extraction_service.py   # LLM structured medicine extraction
│   └── chat_service.py         # LLM-grounded chatbot logic
│
├── tests/
│   └── test_api.py             # Pytest API tests
│
├── .env.example                # Example environment variables
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── LICENSE
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.11+
- pip
- (Optional) Docker & Docker Compose
- An LLM API key (e.g., from [Anthropic Console](https://console.anthropic.com/))

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/PrescriptionLens_AI.git
cd PrescriptionLens_AI
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
Then edit `.env` and add your real API key:
```
LLM_API_KEY=your_real_api_key_here
LLM_MODEL=claude-sonnet-4-6
LLM_API_URL=https://api.anthropic.com/v1/messages
BACKEND_URL=http://localhost:8000
```

**Never commit your `.env` file.** It is already excluded via `.gitignore`.

---

## ▶️ Running Locally

### Start the backend (FastAPI)
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Visit the interactive API docs at: `http://localhost:8000/docs`

### Start the frontend (Streamlit) — in a second terminal
```bash
streamlit run frontend/app.py
```
Visit the app at: `http://localhost:8501`

> Note: the first time EasyOCR runs, it downloads its detection/recognition
> models — this can take a minute and requires internet access.

---

## 🐳 Running with Docker

Build and start both services with Docker Compose:

```bash
docker-compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8501`

Stop the containers:
```bash
docker-compose down
```

Make sure your `.env` file exists in the project root before running
`docker-compose up` — it's loaded via `env_file` in `docker-compose.yml`.

---

## 🔌 API Endpoints

| Method | Endpoint    | Description                                              |
|--------|-------------|-----------------------------------------------------------|
| GET    | `/health`   | Health check                                              |
| POST   | `/ocr`      | Accepts base64 image, runs OpenCV + EasyOCR, returns text |
| POST   | `/analyze`  | Accepts verified prescription text, returns structured medicine JSON |
| POST   | `/chat`     | Accepts a question + prescription context, returns a grounded answer |

Interactive docs are auto-generated by FastAPI at `/docs` (Swagger UI) and `/redoc`.

---

## 🧪 Testing

Run the test suite:
```bash
pytest tests/test_api.py -v
```

Tests cover:
- `/health` returns `200` and status `ok`
- `/analyze` rejects empty prescription text (`400`)
- `/chat` validation for missing/empty fields (`400` / `422`)
- `/ocr` validation for missing image data (`422`)
- Unknown routes return `404`

---

## 🚀 GitHub Setup

```bash
cd PrescriptionLens_AI
git init
git add .
git commit -m "Initial commit: PrescriptionLens AI"
git branch -M main
git remote add origin https://github.com/<your-username>/PrescriptionLens_AI.git
git push -u origin main
```

Before pushing, double check:
```bash
git status        # .env should NOT appear
cat .gitignore    # confirm .env, __pycache__/, venv/ are excluded
```

---

## 🔮 Future Improvements

- Multi-language OCR support (EasyOCR supports many languages)
- PDF prescription upload support
- Export the timing checklist and medicine cards as a PDF/CSV
- Support multiple prescriptions per session with history
- Add user authentication for multi-user deployments
- Add a proper database for persisting checklist progress across sessions
- Improve OCR accuracy with prescription-specific fine-tuning or handwriting models

---

## ⚠️ Medical Safety Disclaimer

This application extracts and organizes information from a prescription and
provides general educational information. It does **not** diagnose conditions
or prescribe/change medication. It is **not** a substitute for professional
medical advice. **Always verify medication instructions with your doctor or
pharmacist**, especially before starting, stopping, or changing any medication.
