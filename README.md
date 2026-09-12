# 🤖 AI-Driven Scheme Matching for Marginalized Entrepreneurs

> **Smart • Inclusive • Personalized Access to Government Schemes**

An AI-powered platform that helps marginalized and underserved entrepreneurs discover **relevant government schemes** by intelligently matching their personal, financial, business, and demographic profiles with verified scheme eligibility criteria.

---

## 🚀 Run Locally

Follow the steps below to run the project on your local machine.

### 📋 Prerequisites

Make sure the following are installed:

* **Python 3.10+**
* **Node.js 18+**
* **npm**
* **MongoDB / MongoDB Atlas**
* **Git**

---

## 📁 Project Structure

```text
AI-driven-scheme-matching-for-marginalized-entrepreneurs/
│
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── .env.example
│   └── ...
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   ├── .env.example
│   └── ...
│
├── ARCHITECTURE.md
├── API.md
├── DEPLOYMENT.md
├── SECURITY.md
├── PRODUCTION_NOTES.md
└── README.md
```

---

# ⚙️ Backend Setup

Open **PowerShell** and run the following commands **one by one**.

### 1. Go to the backend folder

```powershell
cd "D:\AI-Driven Scheme Matching for Marginalized Entrepreneurs\AI-driven-scheme-matching-for-marginalized-entrepreneurs\backend"
```

### 2. Create a Python virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, you should see something similar to:

```text
(.venv) PS D:\AI-Driven Scheme Matching for Marginalized Entrepreneurs\...\backend>
```

### 4. Create the environment configuration file

```powershell
Copy-Item .env.example .env
```

> **Important:** Open the newly created `.env` file and add/update your local configuration such as the MongoDB connection string and JWT secret if required.

### 5. Install backend dependencies

```powershell
pip install -r requirements.txt
```

### 6. Set Python path

```powershell
$env:PYTHONPATH="."
```

### 7. Start the FastAPI backend

```powershell
uvicorn app.main:app --reload
```

The backend should now be available at:

```text
http://127.0.0.1:8000
```

FastAPI API documentation:

```text
http://127.0.0.1:8000/docs
```

Keep this PowerShell window **running** while using the application.

---

# 🎨 Frontend Setup

Open a **new PowerShell window** and run the following commands.

### 1. Go to the frontend folder

```powershell
cd "D:\AI-Driven Scheme Matching for Marginalized Entrepreneurs\AI-driven-scheme-matching-for-marginalized-entrepreneurs\frontend"
```

### 2. Create the frontend environment configuration

```powershell
Copy-Item .env.example .env
```

> **Important:** Check the `.env` file and make sure the API base URL points to your local backend.

For example:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 3. Install frontend dependencies

```powershell
npm install
```

### 4. Start the React development server

```powershell
npm run dev
```

Vite will display a local URL similar to:

```text
http://localhost:5173
```

Open that URL in your browser.

---

# 🖥️ Quick Start

If the project has already been installed once, you normally only need to run these commands.

### Terminal 1 — Backend

```powershell
cd "D:\AI-Driven Scheme Matching for Marginalized Entrepreneurs\AI-driven-scheme-matching-for-marginalized-entrepreneurs\backend"
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH="."
uvicorn app.main:app --reload
```

### Terminal 2 — Frontend

```powershell
cd "D:\AI-Driven Scheme Matching for Marginalized Entrepreneurs\AI-driven-scheme-matching-for-marginalized-entrepreneurs\frontend"
npm run dev
```

Then open:

```text
http://localhost:5173
```

---

# 🧪 Running Tests

From the **project root**, run:

```powershell
$env:PYTHONPATH="backend"
backend\.venv\Scripts\python.exe -m pytest backend/tests -q
```

Or, if you are already inside the backend folder:

```powershell
$env:PYTHONPATH="."
python -m pytest tests -q
```

---

# 🔧 Environment Variables

The project does **not** commit credentials or secrets to GitHub.

Create the required `.env` files from the provided examples:

### Backend

```powershell
cd backend
Copy-Item .env.example .env
```

### Frontend

```powershell
cd frontend
Copy-Item .env.example .env
```

Never commit real:

* MongoDB credentials
* JWT secrets
* API keys
* Passwords
* Private tokens

to the repository.

---

# 🐛 Common Issues

### `uvicorn is not recognized`

Make sure the virtual environment is activated:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then run:

```powershell
uvicorn app.main:app --reload
```

---

### PowerShell blocks virtual environment activation

If PowerShell shows an execution-policy error, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

This changes the policy only for the current PowerShell session.

---

### Frontend cannot connect to backend

Check that:

1. Backend is running.
2. Backend is available at:

```text
http://127.0.0.1:8000
```

3. Frontend `.env` contains the correct API URL:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

4. Restart the frontend after changing `.env`.

---

### MongoDB connection error

Check the backend `.env` configuration and make sure:

* MongoDB is running or MongoDB Atlas is accessible.
* The connection string is correct.
* Database credentials are correct.
* Your MongoDB Atlas IP/network access allows the connection.

---

# 🔄 Development Flow

```text
Start MongoDB
     ↓
Start Backend
     ↓
Start Frontend
     ↓
Open localhost:5173
     ↓
Register / Login
     ↓
Create Entrepreneur Profile
     ↓
Find Matching Schemes
     ↓
View Recommendations
```

---

# 📚 Project Documentation

For detailed technical information, refer to:

* `ARCHITECTURE.md` — System architecture
* `API.md` — API endpoints and contracts
* `DEPLOYMENT.md` — Deployment instructions
* `SECURITY.md` — Security considerations
* `PRODUCTION_NOTES.md` — Production-readiness notes

---

## ⚠️ Disclaimer

This platform provides **informational recommendations only**.

A high match score does not guarantee eligibility, loan approval, subsidy approval, or government benefits.

Users should always verify the latest eligibility requirements and application procedure on the **official government portal** before applying.

---

## 🏆 Smart India Hackathon 2026

**Problem Statement:** SIH26092

**Title:** AI-Driven Scheme Matching for Marginalized Entrepreneurs

> **"No entrepreneur should miss an opportunity simply because they could not find the right scheme."**

Developed as part of **Smart India Hackathon 2026**.
