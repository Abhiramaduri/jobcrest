# JobCrest

JobCrest is an executive job portal platform built with **Django REST Framework** (Backend) and **React + Vite + Tailwind CSS** (Frontend).

---

## 📁 Repository Structure

```text
jobcrest/
├── backend/                  # Django REST API & Database
│   ├── accounts/             # User authentication, profiles, skills
│   ├── applications/         # Job applications & status tracking
│   ├── companies/            # Company & employer profiles
│   ├── config/               # Django settings, WSGI/ASGI, root URLs
│   ├── http_tests/           # REST Client test files (.http)
│   ├── jobs/                 # Job listings, categories, search & filters
│   ├── media/                # User uploaded resumes & files
│   ├── notifications/        # User notifications
│   ├── venv/                 # Python virtual environment
│   ├── db.sqlite3            # SQLite database
│   ├── manage.py             # Django management CLI
│   ├── requirements.txt      # Python dependencies
│   ├── run_api_tests.py      # Automated API test suite
│   └── seed_indian_data.py   # Database seeding script
│
├── frontend/                 # Vite + React SPA
│   ├── node_modules/         # Node dependencies
│   ├── public/               # Static public assets
│   ├── src/                  # React source code (pages, components, context, api)
│   ├── index.html            # HTML entry point
│   ├── package.json          # Frontend scripts & dependencies
│   ├── postcss.config.js     # PostCSS configuration
│   ├── tailwind.config.js    # Tailwind CSS design system configuration
│   └── vite.config.js        # Vite configuration (proxies /api to Django backend)
│
└── README.md
```

---

## 🚀 Getting Started

### 1. Backend Setup (Django)

Open a terminal and navigate to `backend/`:

```bash
cd backend
```

Activate the virtual environment:
- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt):**
  ```cmd
  .\venv\Scripts\activate.bat
  ```
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

*(Optional) Install dependencies if setting up a fresh environment:*
```bash
pip install -r requirements.txt
```

Run database migrations:
```bash
python manage.py migrate
```

Start the Django development server:
```bash
python manage.py runserver
```
The backend API will be available at `http://127.0.0.1:8000/`.

#### Optional Backend Commands:
- **Seed initial data:**
  ```bash
  python seed_indian_data.py
  ```
- **Run automated API tests:**
  ```bash
  python run_api_tests.py
  ```

---

## 💻 2. Frontend Setup (React + Vite)

Open a second terminal and navigate to `frontend/`:

```bash
cd frontend
```

Install dependencies (if not already installed):
```bash
npm install
```

Start the Vite development server:
```bash
npm run dev
```

The frontend will run at `http://localhost:5173/` and automatically proxy API calls (`/api` and `/media`) to the Django server running on `http://127.0.0.1:8000`.

To create a production build:
```bash
npm run build
```
