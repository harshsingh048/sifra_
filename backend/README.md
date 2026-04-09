# Local Freelancing Marketplace - Backend

A production-ready REST API built with **FastAPI** that connects small local businesses with freelancers.

## 🏗️ Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py           # SQLAlchemy engine & session
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py           # User model (client/freelancer)
│   │   ├── task.py           # Task/Post model
│   │   └── application.py    # Application model
│   ├── schemas/              # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   └── application.py
│   ├── routes/               # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py           # /api/auth/*
│   │   ├── users.py          # /api/users/*
│   │   ├── tasks.py          # /api/tasks/*
│   │   ├── applications.py   # /api/applications/*
│   │   └── dashboard.py      # /api/dashboard/*
│   ├── services/             # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── task_service.py
│   │   └── application_service.py
│   ├── core/                 # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py         # Settings & env vars
│   │   └── security.py       # JWT, bcrypt, auth deps
│   └── utils/                # Helper utilities
│       └── __init__.py
├── .env.example              # Environment variables template
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+

### Step 1: Set up the database
```bash
# Create the database
createdb freelance_marketplace

# Or using psql
psql -U postgres
CREATE DATABASE freelance_marketplace;
\q
```

### Step 2: Install dependencies
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Configure environment
```bash
cp .env.example .env
# Edit .env with your actual values
```

### Step 4: Run the server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login with email/password |
| POST | `/api/auth/google` | Login with Google OAuth |
| POST | `/api/auth/refresh` | Refresh access token |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/me` | Get current user profile |
| PUT | `/api/users/me` | Update current user profile |
| GET | `/api/users` | List all users |
| GET | `/api/users/{user_id}` | Get user by ID |

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tasks` | Create a new task (clients only) |
| GET | `/api/tasks` | List all tasks (with filters) |
| GET | `/api/tasks/{task_id}` | Get a single task |
| PUT | `/api/tasks/{task_id}` | Update a task (owner only) |
| DELETE | `/api/tasks/{task_id}` | Delete a task (owner only) |

### Applications
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/applications` | Apply to a task (freelancers only) |
| GET | `/api/applications/task/{task_id}` | View applicants (owner only) |
| PUT | `/api/applications/{app_id}/status` | Accept/reject application |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/my-tasks` | My posted tasks |
| GET | `/api/dashboard/my-applications` | My applied tasks |

## 🔐 Authentication Flow

### Email/Password
1. Register: `POST /api/auth/register`
2. Login: `POST /api/auth/login` → receive `access_token` + `refresh_token`
3. Use token: `Authorization: Bearer <access_token>`
4. Refresh: `POST /api/auth/refresh` when access token expires

### Google OAuth
1. Get Google ID token from frontend (Google Sign-In)
2. Send to: `POST /api/auth/google` with `{ "google_token": "...", "role": "freelancer" }`
3. Receive JWT tokens

## 🧪 Testing with curl

### Register
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@bakery.com",
    "password": "SecurePass123!",
    "role": "client",
    "bio": "Owner of Jane Bakery",
    "company_name": "Jane Bakery"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane@bakery.com",
    "password": "SecurePass123!"
  }'
```

### Create a Task
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Need a Website for My Bakery",
    "description": "Looking for a web developer to build a responsive website...",
    "budget": 1500.00,
    "location": "New York, NY"
  }'
```

### Apply to a Task
```bash
curl -X POST http://localhost:8000/api/applications \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "task_id": "TASK_UUID",
    "cover_letter": "Hi! I am a full-stack developer..."
  }'
```

## 🛡️ Security Features

- **JWT Authentication**: Access tokens (30 min) + Refresh tokens (7 days)
- **Password Hashing**: bcrypt with 12 rounds
- **Role-Based Access**: `client` and `freelancer` roles with route protection
- **Input Validation**: Pydantic schemas on all endpoints
- **CORS Configurable**: Environment-based origin control
- **SQL Injection Prevention**: SQLAlchemy ORM parameterized queries

## 📦 Production Deployment

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with uvicorn (production mode)
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

### Docker (optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📝 License

MIT
