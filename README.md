# 🤖 AI-Driven Scheme Matching for Marginalized Entrepreneurs

> **Smart • Inclusive • Personalized Access to Government Schemes**

An AI-powered platform that helps marginalized and underserved entrepreneurs discover **relevant government schemes** by intelligently matching their personal, financial, business, and demographic profiles with verified scheme eligibility criteria.

## Current Implementation

The repository contains the Phase 1-10 MVP foundation: authenticated user-owned profiles, deterministic eligibility, structured matching, recommendation generation, history, saved schemes, role-protected admin APIs, data-quality checks, and responsive React pages.

```text
frontend/  React + Vite + Tailwind CSS + Axios + React Router
backend/   FastAPI + Pydantic settings + CORS + MongoDB configuration
```

The backend exposes authentication, profile, eligibility, matching, recommendation, history, saved-scheme, scheme-detail, and admin APIs. The Phase 7 semantic service is not present in this repository; semantic and final scores remain null and are not fabricated.

### Run Locally

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Backend:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run tests:

```powershell
$env:PYTHONPATH="backend"
.venv\Scripts\python.exe -m pytest backend/tests -q
```

See [ARCHITECTURE.md](ARCHITECTURE.md), [API.md](API.md), [DEPLOYMENT.md](DEPLOYMENT.md), [SECURITY.md](SECURITY.md), and [PRODUCTION_NOTES.md](PRODUCTION_NOTES.md) for final project documentation.

Copy `frontend/.env.example` and `backend/.env.example` to `.env` files when local configuration is needed. No credentials are committed.

---

## 🏆 Smart India Hackathon 2026

**Problem Statement:** SIH26092
**Title:** AI-Driven Scheme Matching for Marginalized Entrepreneurs

### Theme

**AI-Driven Social Empowerment & Financial Inclusion**

---

## 📌 Problem Statement

India has numerous government schemes designed to support entrepreneurs through:

* Loans
* Subsidies
* Credit support
* Skill development
* Financial assistance
* Infrastructure support
* Entrepreneurship development

However, many marginalized entrepreneurs struggle to access these benefits because:

* Government schemes are spread across multiple portals.
* Eligibility criteria are often complex.
* Entrepreneurs may not know which schemes are relevant to them.
* Searching schemes manually is time-consuming.
* Information is often difficult to understand.
* Schemes may have different eligibility rules based on category, location, income, business type, gender, age, and investment requirements.

As a result, **eligible entrepreneurs may remain unaware of schemes that could support their businesses.**

---

# 💡 Our Solution

We propose an **AI-driven personalized scheme recommendation platform** that analyzes an entrepreneur's profile and identifies government schemes that best match their requirements.

### The platform:

```text
Entrepreneur Profile
        ↓
Data Processing
        ↓
Eligibility Filtering
        ↓
AI-Based Matching
        ↓
Scheme Ranking
        ↓
Explainable Recommendations
        ↓
Official Application Information
```

Instead of simply displaying a list of schemes, our platform answers:

> **"Which government schemes are most relevant to ME, and WHY?"**

---

# 🎯 Objectives

* Simplify access to government schemes.
* Provide personalized scheme recommendations.
* Identify eligibility automatically.
* Reduce information barriers for marginalized entrepreneurs.
* Provide explainable AI-based recommendations.
* Improve financial inclusion.
* Connect users with official scheme information.
* Reduce the time required to find suitable schemes.

---

# 👥 Target Users

The platform primarily focuses on underserved entrepreneurs, including:

* 👩 Women entrepreneurs
* 🏘️ Rural entrepreneurs
* 🧑‍💼 First-time entrepreneurs
* 🏭 Micro and small business owners
* 🧑‍🌾 Rural businesses
* SC/ST entrepreneurs
* OBC entrepreneurs
* Minority entrepreneurs
* Traditional artisans
* Youth entrepreneurs
* Self-help groups and community-based entrepreneurs

---

# 🚀 Key Features

## 1. 👤 Entrepreneur Profiling

Users provide relevant information such as:

* Age
* Gender
* State
* District
* Social category
* Annual income
* Business type
* Business sector
* Business stage
* Rural/Urban location
* Investment requirement
* Loan requirement

---

## 2. 🤖 AI-Based Scheme Matching

The system analyzes the entrepreneur's profile against government scheme information and calculates a relevance score.

Example:

```text
PMEGP
━━━━━━━━━━━━━━━━━━━━
Match Score: 94%

✓ Business type matches
✓ Location matches
✓ Business stage matches
✓ Financial requirement matches
✓ Category benefits applicable
```

---

## 3. 📊 Intelligent Scheme Ranking

Instead of showing hundreds of schemes randomly, the platform ranks them based on relevance.

Example:

| Rank | Scheme         | Match |
| ---- | -------------- | ----: |
| 🥇   | PMEGP          |   94% |
| 🥈   | PMMY           |   89% |
| 🥉   | Stand-Up India |   82% |
| 4    | SVEP           |   78% |

> **Match score is a recommendation score and does not guarantee government approval or eligibility.**

---

## 4. 🔍 Explainable AI

The system explains why a scheme has been recommended.

Example:

```text
Why this scheme?

✓ Your business type is supported
✓ Your location satisfies the requirement
✓ Your age satisfies the eligibility condition
✓ Your investment requirement is compatible
✓ Your applicant category may qualify for additional benefits
```

This makes the recommendation **transparent and understandable**.

---

# 🧠 AI & Matching Methodology

The platform uses a **Hybrid AI + Rule-Based Matching Architecture**.

We do not rely entirely on an LLM.

### Step 1 — Profile Processing

User information is converted into a structured profile.

```text
Age
Gender
Category
Location
Business
Income
Investment
Business Stage
        ↓
Structured User Profile
```

### Step 2 — Hard Eligibility Filtering

Mandatory eligibility conditions are checked first.

For example:

```python
if user.age < scheme.minimum_age:
    return False
```

This prevents obviously incompatible schemes from being recommended.

### Step 3 — Semantic Matching

Natural Language Processing is used to compare:

```text
User Business Profile
        ↕
Scheme Description
```

Embedding models can convert both into vector representations.

Semantic similarity can then be calculated using methods such as **Cosine Similarity**.

### Step 4 — Weighted Ranking

A final recommendation score can combine multiple factors:

```text
Final Score =
40% Eligibility Match
25% Category Match
15% Business Match
10% Location Match
10% Financial Match
```

The weights can be optimized and evaluated during development.

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │       USER          │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   React Frontend    │
                         │   User Dashboard    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    FastAPI / API    │
                         │      Backend        │
                         └──────────┬──────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
           ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
           │ User Data   │   │ Scheme DB   │   │ AI Engine   │
           │             │   │             │   │             │
           └─────────────┘   └─────────────┘   └──────┬──────┘
                                                      │
                                                      ▼
                                            ┌─────────────────┐
                                            │ Eligibility     │
                                            │ Rule Engine     │
                                            └────────┬────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │ Matching &      │
                                            │ Ranking Engine  │
                                            └────────┬────────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │ Recommendations │
                                            │ + Explanation   │
                                            └─────────────────┘
```

---

# 🛠️ Technology Stack

## Frontend

* React.js
* Vite
* Tailwind CSS
* React Router
* Axios
* Recharts

## Backend

* Python
* FastAPI
* Pydantic
* REST APIs

## AI / ML

* Python
* Pandas
* NumPy
* Scikit-learn
* NLP
* Sentence Transformers
* Embedding-based semantic similarity

## Database

* MongoDB
* MongoDB Atlas

## Authentication & Security

* JWT Authentication
* Password Hashing
* Role-Based Access Control
* API Validation
* Environment Variables

## Deployment

* Vercel — Frontend
* Render / Railway — Backend
* MongoDB Atlas — Database

---

# 🗄️ Database Design

## Users

```text
Users
├── _id
├── name
├── age
├── gender
├── category
├── state
├── district
├── income
├── businessType
├── businessStage
├── investment
├── loanRequired
└── locationType
```

## Schemes

```text
Schemes
├── _id
├── name
├── description
├── eligibility
├── categories
├── businessTypes
├── locations
├── benefits
├── documents
├── applicationProcess
├── officialUrl
└── lastVerified
```

## Recommendations

```text
Recommendations
├── _id
├── userId
├── schemeId
├── score
├── reasons
└── generatedAt
```

---

# 🔌 API Structure

## Authentication

```http
POST /api/auth/register
POST /api/auth/login
```

## User

```http
GET /api/user/profile
PUT /api/user/profile
```

## Schemes

```http
GET /api/schemes
GET /api/schemes/:id
```

## Recommendations

```http
POST /api/recommendations
GET /api/recommendations
```

## Admin

```http
POST /api/admin/schemes
PUT /api/admin/schemes/:id
DELETE /api/admin/schemes/:id
```

---

# 📱 Application Flow

```text
        ┌──────────────┐
        │     Start    │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Register /   │
        │ Login        │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Entrepreneur │
        │ Profile      │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Business &   │
        │ Financial    │
        │ Information  │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Find Schemes │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Eligibility  │
        │ Filtering    │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ AI Matching  │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Ranked       │
        │ Schemes      │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Explanation  │
        │ & Benefits   │
        └──────┬───────┘
               ↓
        ┌──────────────┐
        │ Official     │
        │ Application  │
        └──────────────┘
```

---

# 🌟 Innovation

Our platform goes beyond a traditional government-scheme directory.

### Traditional Approach

```text
User
 ↓
Search Government Portal
 ↓
Read Multiple Schemes
 ↓
Manually Check Eligibility
 ↓
Choose Scheme
```

### Our Approach

```text
User Profile
      ↓
AI + Eligibility Engine
      ↓
Personalized Ranking
      ↓
"Why this scheme?"
      ↓
Relevant Government Schemes
```

### Key Innovation

**Personalized + Explainable + Eligibility-Aware Scheme Discovery**

---

# 🌐 Data Reliability

Government scheme information can change over time.

Therefore, each scheme record should maintain:

```text
Scheme Name
Official Source
Eligibility Criteria
Benefits
Documents
Application Process
Last Verified Date
```

The platform should use **official government sources as the source of truth** and direct users to official application portals.

The AI layer is used for **matching, ranking, summarization, and explanation**, not for inventing scheme eligibility.

---

# 🔐 Privacy & Security

The system follows a privacy-first approach.

### Security Measures

* JWT-based authentication
* Password hashing
* Role-based access
* Input validation
* Secure API endpoints
* HTTPS
* Environment variables
* Database access controls

Only information required for scheme matching should be collected.

---

# 📈 Social Impact

The project aims to reduce the information gap between government support programmes and entrepreneurs who need them.

### Expected Impact

```text
Better Awareness
       ↓
Better Scheme Discovery
       ↓
Better Eligibility Understanding
       ↓
Better Access to Support
       ↓
Stronger Entrepreneurship
       ↓
Economic & Social Empowerment
```

---

# 🔮 Future Scope

## 🗣️ Voice-Based Assistant

Users can ask:

> "Mujhe apna business start karne ke liye government se loan chahiye."

The system converts natural language into a structured profile.

---

## 🌍 Multilingual Support

Support for:

* Hindi
* English
* Regional Indian languages

This can improve accessibility for users who are not comfortable with English.

---

## 📄 Document AI

Users could upload relevant documents, and AI can identify:

* Available documents
* Missing documents
* Relevant information
* Potential eligibility requirements

---

## 🔔 Scheme Update Notifications

Users can receive notifications when:

* A new scheme matches their profile.
* Eligibility criteria change.
* Application windows open.
* A recommended scheme is updated.

---

## 📍 Location-Based Recommendations

The platform can combine:

```text
Central Government Schemes
+
State Government Schemes
+
District-Level Schemes
```

to provide more localized recommendations.

---

# 📊 Evaluation Metrics

The AI recommendation system can be evaluated using:

### Precision@K

Measures how many of the top K recommendations are actually relevant.

### Recall@K

Measures how many relevant schemes are successfully retrieved.

### F1 Score

Balances precision and recall.

### User Satisfaction

Collect feedback such as:

```text
Was this recommendation useful?
👍 Yes
👎 No
```

### Explanation Quality

Evaluate whether the reasons shown to the user correctly correspond to the eligibility criteria.

---

# 🧪 Example

### Entrepreneur Profile

```text
Age: 25
Gender: Female
Category: OBC
Location: Rural Uttar Pradesh

Business:
Food Processing

Business Stage:
New

Investment:
₹5,00,000

Loan Requirement:
₹4,00,000
```

### AI Output

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━
🥇 PMEGP
Match Score: 94%
━━━━━━━━━━━━━━━━━━━━━━━━━━

Why?

✓ New enterprise
✓ Supported business category
✓ Rural location
✓ Applicant category may qualify
✓ Financial requirement is compatible

[View Scheme]
```

---

# 🏁 Minimum Viable Product

The SIH prototype focuses on the following core functionality:

* [x] User registration/login
* [x] Entrepreneur profile
* [x] Government scheme database
* [x] Eligibility rule engine
* [x] AI-based matching
* [x] Scheme ranking
* [x] Match score
* [x] Explainable recommendations
* [x] Scheme details
* [x] Official application information
* [x] Admin scheme management

---

# 👨‍💻 Team

### Smart India Hackathon 2026

**Project:** AI-Driven Scheme Matching for Marginalized Entrepreneurs

**Problem Statement:** SIH26092

> Building technology for inclusive entrepreneurship and better access to government support.

---

# 📄 Disclaimer

This platform provides **informational recommendations only**.

A high match score does not guarantee eligibility, loan approval, subsidy approval, or government benefits.

Users should always verify the latest eligibility requirements and application procedure on the **official government portal** before applying.

---

# ⭐ Vision

> **"No entrepreneur should miss an opportunity simply because they could not find the right scheme."**

Our vision is to create an intelligent, inclusive, and transparent bridge between **government support programmes and the entrepreneurs who need them most.**

---

## 📜 License

This project is developed as part of **Smart India Hackathon 2026**.

© 2026 AI-Driven Scheme Matching Team
