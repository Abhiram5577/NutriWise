# 🥗 NutriWise — AI-Powered Nutrition Intelligence System

A full-stack nutrition health application built with React, FastAPI, and PostgreSQL.

## 📋 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite 5 |
| Backend | Python + FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| API Communication | REST (Axios) |

## 🚀 Getting Started

### Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.10
- **PostgreSQL** ≥ 14

### 1. Clone and Navigate

```bash
git clone <your-repo-url>
cd NutriWise
```

### 2. Set Up PostgreSQL

Create a database named `nutriwise`:

```sql
CREATE DATABASE nutriwise;
```

Update `backend/.env` with your credentials if they differ from the defaults:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nutriwise
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be available at **http://localhost:8000**.
Interactive docs at **http://localhost:8000/docs**.

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at **http://localhost:5173**.

## 🔍 API Endpoints

### Health Checks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Server health check |
| GET | `/api/health/db` | Database connectivity check |

### Authentication (Stubs)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register (coming soon) |
| POST | `/api/auth/login` | Login (coming soon) |

### Food Diary (CRUD)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/food-diary` | List entries |
| GET | `/api/food-diary/:id` | Get entry |
| POST | `/api/food-diary` | Create entry |
| PUT | `/api/food-diary/:id` | Update entry |
| DELETE | `/api/food-diary/:id` | Delete entry |

### Health Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health-profile` | Get profile |
| POST | `/api/health-profile` | Create profile |
| PUT | `/api/health-profile` | Update profile |

### Symptoms
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/symptoms` | List symptoms |
| POST | `/api/symptoms` | Record symptom |
| DELETE | `/api/symptoms/:id` | Delete symptom |

### Lab Results
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lab-results` | List results |
| POST | `/api/lab-results` | Add result |
| PUT | `/api/lab-results/:id` | Update result |
| DELETE | `/api/lab-results/:id` | Delete result |

## 📁 Project Structure

```
NutriWise/
├── frontend/           # React + Vite
│   ├── src/
│   │   ├── api/        # Axios client
│   │   ├── components/ # Reusable UI
│   │   └── pages/      # Route pages
│   └── ...
├── backend/            # Python FastAPI
│   ├── app/
│   │   ├── models/     # SQLAlchemy ORM
│   │   ├── schemas/    # Pydantic validation
│   │   └── routers/    # API endpoints
│   └── ...
└── README.md
```

## 🗄️ Database Tables

| Table | Purpose |
|-------|---------|
| `users` | User accounts and auth |
| `health_profiles` | Biometrics and preferences |
| `food_diary_entries` | Meal logs with nutrients |
| `symptoms` | Health symptom tracking |
| `lab_results` | Blood/lab test values |

## 🔒 Environment Variables

All secrets are loaded from `.env` files. **Never commit real credentials.**

### Backend (`backend/.env`)
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nutriwise
SECRET_KEY=your-secret-key
NUTRITION_API_KEY=your-api-key
```

### Frontend (`frontend/.env`)
```
VITE_API_URL=http://localhost:8000
```

## 📌 Current Status: Week 1 & Week 2 (100% Complete)

✅ Project structure & decoupled architecture  
✅ FastAPI backend with CORS & JWT Authentication  
✅ PostgreSQL connection + ORM models (Users, Health Profile, Food Diary, Symptoms, Lab Results)  
✅ User registration and login flows with password hashing  
✅ Complete Health Profile Module (Age, Gender, Height, Weight, Conditions, Allergies, Goals)  
✅ Interactive Food Diary UI with full CRUD operations  
✅ Daily macro & micronutrient totals calculation  
✅ Nutrition API integration (Open Food Facts + USDA standard baseline reference)  
✅ Clinical symptom assessment questionnaire (Fatigue, Hair loss, Skin conditions, Muscle weakness, Mood-related symptoms)  
✅ Structured blood test input panels (Hemoglobin, Vitamin D, Vitamin B12, Iron, Calcium)  
✅ Cross-user security and full data isolation  
  
