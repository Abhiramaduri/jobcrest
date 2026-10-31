<div align="center">

<img src="https://img.shields.io/badge/JobCrest-Executive%20Job%20Portal-8B1A2E?style=for-the-badge&logoColor=white" alt="JobCrest" />

# 🏔️ JobCrest

### *Where Top Talent Meets Elite Opportunity*

A full-stack **executive job portal** connecting India's best engineers, designers, and product managers with high-growth tech companies like Razorpay, CRED, Zerodha, Flipkart, and more.

<br/>

[![Django](https://img.shields.io/badge/Django-6.1-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.18-ff1709?style=flat-square&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-336791?style=flat-square&logo=postgresql&logoColor=white)](https://supabase.com/)
[![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=flat-square&logo=json-web-tokens&logoColor=white)](https://jwt.io/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)

<br/>

[🚀 Live Demo](#-live-demo) · [📖 API Docs](#-api-endpoints) · [⚙️ Setup Guide](#-getting-started) · [🤝 Contributing](#-contributing)

---

</div>

## 📸 Screenshots

> *JobCrest — Premium job portal built for India's elite tech ecosystem*

| Job Seeker Dashboard | Employer Dashboard | Job Listings |
|:---:|:---:|:---:|
| Applications tracking, interviews & bookmarks | Post jobs, review applicants, schedule interviews | Filter by category, salary, location & skills |

---

## ✨ Features

<details>
<summary><b>👤 Authentication & User Management</b></summary>

- **Dual role system** — Job Seekers & Employers with separate onboarding flows
- **JWT-based authentication** with access + refresh token rotation
- Secure password hashing via Django's built-in PBKDF2 algorithm
- Token blacklisting on logout for maximum security
- Email verification flag (`is_verified`) for account quality control

</details>

<details>
<summary><b>🧑‍💼 Job Seeker Features</b></summary>

- **Rich profile** with headline, bio, location, CTC range (current & expected), LinkedIn, GitHub
- **Resume upload** (PDF/DOC via media storage)
- **Skills management** with proficiency levels (`Beginner` / `Intermediate` / `Expert`)
- **Education & Experience** timeline with multiple entries
- **Job search & filters** — by category, job type, salary range, location, remote, skills
- **Save / bookmark** jobs for later
- **Application tracking** — view real-time status updates (`Applied → Under Review → Shortlisted → Interview → Hired`)
- **Interview inbox** — see scheduled virtual, in-person, or phone interviews
- **Notifications feed** — application updates, interview invitations, job match alerts

</details>

<details>
<summary><b>🏢 Employer Features</b></summary>

- **Company profile** — logo, industry, size, founded year, website, description
- **Job post wizard** — multi-step form with rich job description, responsibilities, requirements
- **Applicant management** — view all applicants per job, review profiles & resumes
- **Status updates** — move candidates through hiring pipeline with notes
- **Interview scheduler** — virtual (Google Meet / Zoom), in-person, or phone with agenda notes
- **Application audit history** — full log of every status change with timestamps

</details>

<details>
<summary><b>🔎 Jobs & Discovery</b></summary>

- **8 job categories** — Software Engineering, Data Science & AI, Cloud & DevOps, UI/UX, Product Management, Marketing, Finance, Sales
- **Powerful filtering** — job type, salary min/max, experience range, remote/onsite, skills, location
- **Search** by title, company, or keyword
- **Ordering** by date posted, salary, or experience
- **Slug-based SEO-friendly URLs** for jobs and companies

</details>

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|:---|:---|
| **Django 6.1** | Web framework & ORM |
| **Django REST Framework 3.18** | RESTful API layer |
| **Simple JWT** | Access & Refresh token auth |
| **django-cors-headers** | Cross-origin request handling |
| **django-filter** | Advanced query filtering |
| **psycopg2-binary** | PostgreSQL adapter |
| **Pillow** | Image processing (logos, profile pics) |
| **python-decouple** | Environment variable management |
| **Gunicorn** | Production WSGI server |
| **WhiteNoise** | Static file serving in production |

### Frontend
| Technology | Purpose |
|:---|:---|
| **React 18** | UI component framework |
| **Vite 6** | Lightning-fast dev server & bundler |
| **Tailwind CSS 3.4** | Utility-first design system |
| **React Router DOM 6** | Client-side routing |
| **Axios** | HTTP client with interceptors |
| **React Hook Form** | Performant form management |
| **React Hot Toast** | Elegant toast notifications |
| **Lucide React** | Icon library |

### Infrastructure
| Service | Role |
|:---|:---|
| **Supabase PostgreSQL** | Production cloud database |
| **GitHub** | Version control & CI/CD |

---

## 📁 Project Structure

```
jobcrest/
├── 📁 backend/                        # Django REST API
│   ├── 📁 accounts/                   # Auth, users, profiles, skills, education, experience
│   ├── 📁 applications/               # Applications, status history, interviews
│   ├── 📁 companies/                  # Company profiles & employer accounts
│   ├── 📁 jobs/                       # Job listings, categories, saved jobs
│   ├── 📁 notifications/              # In-app notification system
│   ├── 📁 config/                     # Django settings, URLs, WSGI/ASGI
│   ├── 📁 http_tests/                 # .http REST Client test files
│   ├── 📄 manage.py                   # Django CLI
│   ├── 📄 requirements.txt            # Python dependencies
│   ├── 📄 Dockerfile                  # Container deployment config
│   ├── 📄 seed_indian_data.py         # Initial Indian company & job seed data
│   ├── 📄 seed_more_dummy_data.py     # Extended dummy data (20 jobs, 13 companies)
│   └── 📄 run_api_tests.py            # Automated API test suite
│
├── 📁 frontend/                       # React + Vite SPA
│   └── 📁 src/
│       ├── 📁 api/                    # Axios API client modules
│       │   ├── axiosInstance.js       # Base Axios config & interceptors
│       │   ├── authApi.js             # Login, register, logout
│       │   ├── jobsApi.js             # Job CRUD & search
│       │   ├── applicationsApi.js     # Applications & interviews
│       │   ├── profileApi.js          # Job seeker profile management
│       │   └── companyApi.js          # Company & employer profile
│       ├── 📁 components/
│       │   ├── applications/          # ApplicantDetailModal, InterviewScheduleModal
│       │   ├── common/                # Navbar, Footer, Button, Input, Modal, Badge
│       │   ├── jobs/                  # JobCard, ApplyModal, JobFilterSidebar
│       │   └── profile/               # EducationCard, ExperienceCard, SkillsEditor, ResumeUploader
│       ├── 📁 context/                # AuthContext (global auth state)
│       ├── 📁 hooks/                  # useAuth, useJobs, useDebounce
│       ├── 📁 layouts/               # MainLayout, DashboardLayout, AuthLayout
│       ├── 📁 pages/                  # Home, Jobs, JobDetail, Applications, Profile...
│       └── 📁 routes/                 # AppRoutes, ProtectedRoute
│
├── 📄 Dockerfile                      # Root-level Docker build
├── 📄 .gitignore
└── 📄 README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **Node.js 18+** and **npm**
- **PostgreSQL** (or a [Supabase](https://supabase.com) account for cloud DB)
- **Git**

---

### ⚙️ Backend Setup (Django)

**1. Clone the repository**
```bash
git clone https://github.com/Abhiramaduri/jobcrest.git
cd jobcrest
```

**2. Create and activate a virtual environment**

```bash
# Navigate to the backend
cd backend

# Create virtualenv
python -m venv venv

# Activate it
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (CMD):
.\venv\Scripts\activate.bat

# macOS / Linux:
source venv/bin/activate
```

**3. Install Python dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file inside `backend/`:
```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL (Supabase or local)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=your-supabase-host.supabase.co
DB_PORT=5432
DB_SSLMODE=require

# CORS
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

**5. Run migrations**
```bash
python manage.py migrate
```

**6. (Optional) Seed dummy data**
```bash
# Seed initial Indian companies, jobs & test accounts:
python seed_indian_data.py

# Seed extended dummy data (20 jobs, 13 companies, 6 candidates):
python seed_more_dummy_data.py
```

**7. Start the development server**
```bash
python manage.py runserver
```

✅ Backend API running at: **http://127.0.0.1:8000/**

---

### 💻 Frontend Setup (React + Vite)

**Open a second terminal** from the project root:

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend running at: **http://localhost:5173/**

> Vite automatically proxies `/api/*` and `/media/*` requests to `http://127.0.0.1:8000` — no CORS issues in development.

---

## 🌐 API Endpoints

<details>
<summary><b>🔐 Authentication</b></summary>

| Method | Endpoint | Description |
|:---:|:---|:---|
| `POST` | `/api/register/` | Register new user (jobseeker or employer) |
| `POST` | `/api/login/` | Login → returns access & refresh tokens |
| `POST` | `/api/logout/` | Blacklist refresh token |
| `POST` | `/api/auth/refresh/` | Refresh access token |
| `GET` | `/api/me/` | Get current authenticated user info |

</details>

<details>
<summary><b>👤 Profiles</b></summary>

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET/PUT` | `/api/profile/jobseeker/` | Get or update job seeker profile |
| `GET/PUT` | `/api/profile/employer/` | Get or update employer profile |
| `GET/POST` | `/api/profile/skills/` | List or add skills |
| `DELETE` | `/api/profile/skills/<id>/` | Remove a skill |
| `GET/POST` | `/api/profile/education/` | List or add education entries |
| `GET/POST` | `/api/profile/experience/` | List or add experience entries |
| `POST` | `/api/profile/resume/` | Upload resume file |

</details>

<details>
<summary><b>💼 Jobs</b></summary>

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET` | `/api/jobs/` | List all published jobs (with filters & search) |
| `POST` | `/api/jobs/` | Create a new job posting (Employer only) |
| `GET` | `/api/jobs/<slug>/` | Get job detail |
| `PUT/PATCH` | `/api/jobs/<slug>/` | Update job (Employer only) |
| `DELETE` | `/api/jobs/<slug>/` | Delete job (Employer only) |
| `GET` | `/api/jobs/categories/` | List all job categories |
| `GET/POST` | `/api/jobs/saved/` | Get or save a bookmarked job |
| `DELETE` | `/api/jobs/saved/<id>/` | Remove a saved job |

</details>

<details>
<summary><b>📄 Applications</b></summary>

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET/POST` | `/api/applications/` | List own applications or submit new one |
| `GET` | `/api/applications/<id>/` | Get application detail |
| `PATCH` | `/api/applications/<id>/status/` | Update application status (Employer) |
| `GET` | `/api/applications/employer/` | List all applicants for employer's jobs |
| `POST` | `/api/applications/interviews/` | Schedule an interview |
| `GET` | `/api/applications/interviews/` | List upcoming interviews |

</details>

<details>
<summary><b>🏢 Companies</b></summary>

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET` | `/api/companies/` | List all companies |
| `GET` | `/api/companies/<slug>/` | Get company detail with open jobs |
| `POST/PUT` | `/api/companies/` | Create or update company (Employer) |

</details>

---

## 🧪 Test Accounts

All test accounts use password: **`TestPass@123`**

### 👨‍💻 Job Seekers
| Username | Profile | Background |
|:---|:---|:---|
| `rohan_dev` | Senior Full Stack Engineer | BITS Pilani |
| `ananya_design` | Product Designer | NID Ahmedabad |
| `vikram_cloud` | DevOps / SRE | IIT Madras |
| `priya_fullstack` | Lead Full Stack, Ex-Swiggy | NIT Trichy |
| `karthik_ai` | ML Engineer / GenAI | IIT Hyderabad |
| `tanvi_product` | Senior Product Manager | IIM Ahmedabad |

### 🏢 Employers / Recruiters
| Username | Company |
|:---|:---|
| `razorpay_recruiter` | Razorpay Software |
| `zerodha_talent` | Zerodha Broking |
| `cred_hiring` | CRED (Dreamplug Tech) |
| `swiggy_hiring` | Swiggy Technologies |
| `flipkart_recruiter` | Flipkart Internet |
| `phonepe_recruiter` | PhonePe Technologies |
| `postman_recruiter` | Postman Software |
| `groww_recruiter` | Groww (Nextbillion Tech) |
| `zomato_recruiter` | Zomato Ltd |
| `hasura_recruiter` | Hasura India |

---

## 🗄️ Database Schema (Overview)

```
User ──────────────────┬── JobSeekerProfile ──── Skills, Education, Experience
     (AbstractUser)    │
                       └── EmployerProfile ────── Company

JobCategory ───── Job ──────────────── Application ──── ApplicationStatusHistory
                  │                        │
                  └── SavedJob             └── Interview

User ──── Notification
```

---

## 🐳 Docker Deployment

A `Dockerfile` is included for containerized deployments (Koyeb, Railway, Render, etc.):

```bash
# Build the image
docker build -t jobcrest-backend .

# Run with environment variables
docker run -p 8000:8000 \
  -e SECRET_KEY=your-key \
  -e DB_HOST=your-supabase-host \
  -e DB_PASSWORD=your-password \
  jobcrest-backend
```

---

## 🌍 Deployment Guides

<details>
<summary><b>Koyeb (Free, No Credit Card)</b></summary>

1. Push code to GitHub
2. Go to [koyeb.com](https://koyeb.com) → Create App → GitHub source
3. Select repo `Abhiramaduri/jobcrest`, branch `main`
4. Port: `8000`, Dockerfile: auto-detected
5. Add all environment variables
6. Deploy ✅

</details>

<details>
<summary><b>Render (Free Tier)</b></summary>

- **Root Directory:** `backend`
- **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
- **Start Command:** `gunicorn config.wsgi:application`
- Add environment variables in the Render dashboard

</details>

---

## 🤝 Contributing

Contributions are welcome! Here's how:

```bash
# Fork & clone
git clone https://github.com/Abhiramaduri/jobcrest.git

# Create a feature branch
git checkout -b feature/your-feature-name

# Make changes, commit
git commit -m "feat: add your feature"

# Push & open a PR
git push origin feature/your-feature-name
```

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

Built with ❤️ by **[Abhiram Aduri](https://github.com/Abhiramaduri)**

⭐ Star this repo if you find it useful!

</div>
