import os
import django
from datetime import datetime, timedelta, date
from django.utils import timezone
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, JobSeekerProfile, Skill, JobSeekerSkill, Education, Experience
from companies.models import Company, EmployerProfile
from jobs.models import JobCategory, Job, SavedJob
from applications.models import Application, ApplicationStatusHistory, Interview

def seed():
    print("Starting Indian Data Seeding for JobCrest...")

    # 1. Categories
    categories_data = [
        "Software Engineering",
        "Product Management",
        "UI/UX & Product Design",
        "Data Science & AI",
        "Cloud & DevOps",
        "Marketing & Growth",
        "Finance & FinTech Operations",
        "Sales & Strategic Partnerships"
    ]
    categories = {}
    for cat_name in categories_data:
        cat, _ = JobCategory.objects.get_or_create(name=cat_name)
        categories[cat_name] = cat
    print(f"[OK] Seeded {len(categories)} job categories")

    # 2. Skills
    skills_data = [
        "Python", "Django", "React.js", "TypeScript", "Node.js", "Next.js",
        "PostgreSQL", "MongoDB", "Redis", "AWS", "Docker", "Kubernetes",
        "Apache Kafka", "Java", "Spring Boot", "Machine Learning", "PyTorch",
        "LLMs & GenAI", "Figma", "UI/UX Prototyping", "Go (Golang)", "GraphQL",
        "Tailwind CSS", "Microservices Architecture", "System Design", "SQL"
    ]
    skills = {}
    for s_name in skills_data:
        sk, _ = Skill.objects.get_or_create(name=s_name)
        skills[s_name] = sk
    print(f"[OK] Seeded {len(skills)} technical skills")

    # 3. Companies & Employers
    companies_data = [
        {
            "name": "Razorpay Software",
            "industry": "FinTech & Payments",
            "company_size": "500+",
            "founded_year": 2014,
            "location": "Bengaluru, Karnataka",
            "website": "https://razorpay.com",
            "description": "Razorpay is India's leading full-stack financial solutions company, empowering millions of businesses with automated payments, neo-banking, and payroll infrastructure.",
            "recruiter_username": "razorpay_recruiter",
            "recruiter_email": "careers@razorpay.com",
            "recruiter_name": "Kavita Narayanan",
            "designation": "Director of Talent Acquisition",
        },
        {
            "name": "Zerodha Broking",
            "industry": "FinTech & WealthTech",
            "company_size": "500+",
            "founded_year": 2010,
            "location": "Bengaluru, Karnataka",
            "website": "https://zerodha.com",
            "description": "Zerodha is India's largest retail stockbroker by active client base. Renowned for its lean engineering culture, open-source adoption, and zero brokerage investments.",
            "recruiter_username": "zerodha_talent",
            "recruiter_email": "jobs@zerodha.com",
            "recruiter_name": "Aditya Hegde",
            "designation": "Head of Engineering Hiring",
        },
        {
            "name": "Swiggy Technologies",
            "industry": "FoodTech & Quick Commerce",
            "company_size": "500+",
            "founded_year": 2014,
            "location": "Bengaluru, Karnataka",
            "website": "https://swiggy.com",
            "description": "Swiggy is India’s pioneering on-demand delivery platform, powering Instamart and food delivery with ultra-scalable distributed logistics algorithms.",
            "recruiter_username": "swiggy_hiring",
            "recruiter_email": "talent@swiggy.in",
            "recruiter_name": "Manish Sen",
            "designation": "Staff Technical Recruiter",
        },
        {
            "name": "CRED (Dreamplug Tech)",
            "industry": "FinTech & Lifestyle",
            "company_size": "201-500",
            "founded_year": 2018,
            "location": "Bengaluru, Karnataka",
            "website": "https://cred.club",
            "description": "CRED is an exclusive members-only community celebrating creditworthy individuals with bespoke rewards, seamless peer-to-peer payments, and luxury commerce.",
            "recruiter_username": "cred_hiring",
            "recruiter_email": "careers@cred.club",
            "recruiter_name": "Pooja Deshmukh",
            "designation": "People Partner & Hiring Lead",
        },
        {
            "name": "Postman Labs",
            "industry": "Developer Tools & SaaS",
            "company_size": "500+",
            "founded_year": 2014,
            "location": "Bengaluru & Remote",
            "website": "https://postman.com",
            "description": "Postman is the world’s leading API collaboration platform used by over 30 million developers across global technology organizations.",
            "recruiter_username": "postman_talent",
            "recruiter_email": "jobs@postman.com",
            "recruiter_name": "Siddharth Rao",
            "designation": "Lead Tech Recruiter",
        },
        {
            "name": "Urban Company",
            "industry": "Home Services Marketplace",
            "company_size": "500+",
            "founded_year": 2014,
            "location": "Gurugram, Haryana",
            "website": "https://urbancompany.com",
            "description": "Urban Company is Asia's largest home services marketplace connecting consumers with verified beauty, maintenance, and wellness professionals.",
            "recruiter_username": "urban_recruiter",
            "recruiter_email": "hiring@urbancompany.com",
            "recruiter_name": "Ananya Bansal",
            "designation": "Senior HR Manager",
        }
    ]

    employers = []
    for comp_data in companies_data:
        # Create recruiter user
        user, _ = User.objects.get_or_create(
            username=comp_data["recruiter_username"],
            defaults={
                "email": comp_data["recruiter_email"],
                "user_type": "employer",
                "phone_number": "+91 98765 43210",
                "is_verified": True
            }
        )
        user.set_password("TestPass@123")
        user.save()

        # Create Company
        company, _ = Company.objects.get_or_create(
            name=comp_data["name"],
            defaults={
                "industry": comp_data["industry"],
                "company_size": comp_data["company_size"],
                "founded_year": comp_data["founded_year"],
                "location": comp_data["location"],
                "website": comp_data["website"],
                "description": comp_data["description"],
                "created_by": user
            }
        )

        # Employer Profile
        emp_profile, _ = EmployerProfile.objects.get_or_create(
            user=user,
            defaults={
                "company": company,
                "designation": comp_data["designation"],
                "is_company_admin": True
            }
        )
        employers.append(emp_profile)

    print(f"[OK] Seeded {len(companies_data)} verified Indian companies & recruiters")

    # 4. Jobs across Indian Tech hubs
    jobs_data = [
        {
            "employer_idx": 0, # Razorpay
            "category": "Software Engineering",
            "title": "Lead Backend Platform Architect (Python & Django)",
            "job_type": "full-time",
            "location": "Bengaluru, Karnataka",
            "is_remote": False,
            "experience_min": 6,
            "experience_max": 10,
            "salary_min": Decimal("3200000"),
            "salary_max": Decimal("4800000"),
            "vacancies": 3,
            "skills": ["Python", "Django", "PostgreSQL", "Redis", "Apache Kafka", "System Design"],
            "description": "Razorpay's Payment Platform team processes millions of transactions every hour. As a Lead Backend Architect, you will own transaction reliability, sub-50ms gateway orchestration, and fault-tolerant ledger systems.",
            "responsibilities": "- Architect and optimize high-throughput distributed microservices in Python & Go.\n- Lead architectural reviews for zero-downtime database migrations on multi-terabyte PostgreSQL clusters.\n- Partner with InfoSec to ensure strict PCI-DSS & RBI banking compliance.\n- Mentor senior engineers on high-concurrency distributed caching using Redis.",
            "requirements": "- 6+ years designing mission-critical distributed systems in Python/Django or Go.\n- Deep mastery of ACID transactions, event-driven architectures (Kafka), and distributed tracing.\n- B.Tech/M.Tech in Computer Science from a reputable institution.",
            "deadline": date.today() + timedelta(days=45)
        },
        {
            "employer_idx": 3, # CRED
            "category": "UI/UX & Product Design",
            "title": "Staff Product Designer (Luxury Aesthetics & Mobile)",
            "job_type": "full-time",
            "location": "Bengaluru, Karnataka",
            "is_remote": True,
            "experience_min": 5,
            "experience_max": 8,
            "salary_min": Decimal("2800000"),
            "salary_max": Decimal("4400000"),
            "vacancies": 2,
            "skills": ["Figma", "UI/UX Prototyping"],
            "description": "CRED’s design team sets the global benchmark for dark-mode luxury aesthetics, spatial depth, and tactile haptic micro-interactions. You will define the future of high-trust member experiences.",
            "responsibilities": "- Craft immaculate visual systems, typographic hierarchies, and haptic animations for CRED Pay and Store.\n- Collaborate closely with iOS/Android engineers to realize 60fps vector fluid animations.\n- Conduct customer immersion interviews with creditworthy members across tier-1 Indian metros.",
            "requirements": "- Outstanding design portfolio showing luxury visual craft, typography, and motion prototypes.\n- 5+ years building consumer mobile apps at scale.\n- Obsessive attention to pixel precision, color contrast, and ergonomics.",
            "deadline": date.today() + timedelta(days=30)
        },
        {
            "employer_idx": 1, # Zerodha
            "category": "Software Engineering",
            "title": "Senior Systems Engineer (Go & PostgreSQL)",
            "job_type": "full-time",
            "location": "Bengaluru, Karnataka",
            "is_remote": False,
            "experience_min": 4,
            "experience_max": 7,
            "salary_min": Decimal("2600000"),
            "salary_max": Decimal("4000000"),
            "vacancies": 2,
            "skills": ["Go (Golang)", "PostgreSQL", "Redis", "Microservices Architecture", "System Design"],
            "description": "Kite by Zerodha executes over 15% of all Indian stock market trades daily. We believe in small, autonomous teams, radical simplicity, zero meetings, and raw open-source power.",
            "responsibilities": "- Maintain low-latency order-routing engines handling peak market volatility.\n- Optimize PostgreSQL queries and indexes for high-frequency market data streams.\n- Contribute upstream fixes to open-source libraries used in production.",
            "requirements": "- 4+ years building high-performance systems in Go, C, or Python.\n- Strong comprehension of OS concurrency primitives, memory management, and network I/O.\n- Deep respect for clean, dependency-minimalist code.",
            "deadline": date.today() + timedelta(days=60)
        },
        {
            "employer_idx": 2, # Swiggy
            "category": "Data Science & AI",
            "title": "Principal Machine Learning Engineer (Dispatch & ETA)",
            "job_type": "full-time",
            "location": "Bengaluru, Karnataka",
            "is_remote": False,
            "experience_min": 7,
            "experience_max": 12,
            "salary_min": Decimal("4200000"),
            "salary_max": Decimal("6500000"),
            "vacancies": 2,
            "skills": ["Python", "Machine Learning", "PyTorch", "LLMs & GenAI", "Apache Kafka"],
            "description": "Swiggy processes tens of millions of hyperlocal orders weekly. Our AI engine dynamically computes delivery partner dispatches, prep-time predictions, and routing optimizations in real-time.",
            "responsibilities": "- Lead algorithmic improvements for 10-minute Instamart order routing and surge forecasting.\n- Deploy large-scale neural network models on GPU clusters with sub-20ms inference latency.\n- Collaborate with operations research scientists on spatial graph neural networks.",
            "requirements": "- 7+ years production ML experience, with focus on graph networks, reinforcement learning, or spatial models.\n- Track record of shipping models generating quantifiable revenue/efficiency impact.\n- Degree in CS, Operations Research, or Statistics (IIT/IISc or equivalent preferred).",
            "deadline": date.today() + timedelta(days=35)
        },
        {
            "employer_idx": 4, # Postman
            "category": "Software Engineering",
            "title": "Staff Full Stack Engineer (React, TypeScript & Node.js)",
            "job_type": "full-time",
            "location": "Bengaluru / Hyderabad (Hybrid)",
            "is_remote": True,
            "experience_min": 5,
            "experience_max": 9,
            "salary_min": Decimal("3000000"),
            "salary_max": Decimal("4600000"),
            "vacancies": 4,
            "skills": ["React.js", "TypeScript", "Node.js", "Next.js", "GraphQL", "Tailwind CSS"],
            "description": "Postman's API Platform is utilized by developers in 98% of the Fortune 500. Join our API Network team to build blazing-fast developer tooling and real-time collaboration canvas.",
            "responsibilities": "- Build complex, high-performance desktop and web UI workflows using React 18 & TypeScript.\n- Optimize virtualized trees, Monaco code editors, and real-time WebSockets synchronization.\n- Drive frontend architectural standards and design system consistency across distributed teams.",
            "requirements": "- 5+ years of intense modern frontend engineering with React, TypeScript, and state architectures.\n- Deep understanding of browser rendering pipelines, Web Workers, and bundle optimization.\n- Active open-source contributions or experience with developer tooling.",
            "deadline": date.today() + timedelta(days=40)
        },
        {
            "employer_idx": 5, # Urban Company
            "category": "Product Management",
            "title": "Director of Product (Partner Ecosystem & Marketplace)",
            "job_type": "full-time",
            "location": "Gurugram, Haryana",
            "is_remote": False,
            "experience_min": 7,
            "experience_max": 12,
            "salary_min": Decimal("4000000"),
            "salary_max": Decimal("6000000"),
            "vacancies": 1,
            "skills": ["System Design", "SQL"],
            "description": "Urban Company empowers over 50,000 service partners across India with dignity and middle-class earnings. Lead product strategy for partner onboarding, training gamification, and automated earnings payout.",
            "responsibilities": "- Define the 3-year product roadmap for partner lifecycle and quality assurance algorithms.\n- Translate complex behavioral data from hundreds of Indian cities into crisp feature specs.\n- Work in tight sync with C-suite leadership and city operations teams.",
            "requirements": "- 7+ years in product management with at least 3 years scaling two-sided marketplaces.\n- Strong quantitative intuition, SQL fluency, and empathetic customer-first mindset.\n- Tier-1 MBA (IIM / ISB) or equivalent engineering leadership background.",
            "deadline": date.today() + timedelta(days=30)
        },
        {
            "employer_idx": 0, # Razorpay
            "category": "Cloud & DevOps",
            "title": "Senior Cloud Infrastructure Engineer (Kubernetes & AWS)",
            "job_type": "full-time",
            "location": "Bengaluru, Karnataka",
            "is_remote": True,
            "experience_min": 4,
            "experience_max": 8,
            "salary_min": Decimal("2500000"),
            "salary_max": Decimal("3800000"),
            "vacancies": 2,
            "skills": ["AWS", "Docker", "Kubernetes", "Redis"],
            "description": "Scale Razorpay's multi-region AWS cloud infrastructure handling thousands of RPS with five-nines (99.999%) availability.",
            "responsibilities": "- Manage multi-cluster Kubernetes deployments (EKS) with automated blue-green pipelines.\n- Implement infrastructure-as-code (Terraform) and comprehensive Prometheus/Grafana monitoring.\n- Lead chaos engineering experiments to harden our disaster recovery posture.",
            "requirements": "- 4+ years operating production Kubernetes workloads on AWS.\n- Hands-on expertise with Terraform, service meshes (Istio), and CI/CD pipelines.",
            "deadline": date.today() + timedelta(days=50)
        },
        {
            "employer_idx": 3, # CRED
            "category": "Marketing & Growth",
            "title": "Growth Marketing Lead (Brand Campaigns & Acquisition)",
            "job_type": "full-time",
            "location": "Bengaluru, Karnataka",
            "is_remote": False,
            "experience_min": 4,
            "experience_max": 7,
            "salary_min": Decimal("2000000"),
            "salary_max": Decimal("3200000"),
            "vacancies": 2,
            "skills": ["SQL"],
            "description": "CRED’s marketing campaigns are cultural phenomena in India. Lead performance marketing, IPL sponsorships integration, and viral member referral engines.",
            "responsibilities": "- Own multi-crore digital growth budgets across search, programmatic, and viral loops.\n- Formulate A/B testing hypotheses on conversion funnels and CAC efficiency.\n- Work with creative copywriters and influencers to orchestrate memorable launches.",
            "requirements": "- 4+ years driving exponential user growth at a top Indian B2C consumer tech brand.\n- Ruthless data-driven rigor, cohort analytics, and high aesthetic sensibilities.",
            "deadline": date.today() + timedelta(days=25)
        }
    ]

    created_jobs = []
    for jd in jobs_data:
        emp = employers[jd["employer_idx"]]
        cat = categories[jd["category"]]
        job, created = Job.objects.get_or_create(
            title=jd["title"],
            company=emp.company,
            defaults={
                "posted_by": emp,
                "category": cat,
                "job_type": jd["job_type"],
                "location": jd["location"],
                "is_remote": jd["is_remote"],
                "experience_min": jd["experience_min"],
                "experience_max": jd["experience_max"],
                "salary_min": jd["salary_min"],
                "salary_max": jd["salary_max"],
                "salary_currency": "INR",
                "vacancies": jd["vacancies"],
                "description": jd["description"],
                "responsibilities": jd["responsibilities"],
                "requirements": jd["requirements"],
                "status": "published",
                "application_deadline": jd["deadline"],
                "views_count": 142
            }
        )
        for s_name in jd["skills"]:
            if s_name in skills:
                job.skill_required.add(skills[s_name])
        created_jobs.append(job)

    print(f"[OK] Seeded {len(created_jobs)} high-value Indian tech positions")

    # 5. Job Seekers
    seekers_data = [
        {
            "username": "rohan_dev",
            "email": "rohan.sharma@example.com",
            "full_name": "Rohan Sharma",
            "headline": "Senior Full Stack Engineer | Python, React & Distributed Systems",
            "location": "Bengaluru, Karnataka",
            "experience_years": 5,
            "current_ctc": Decimal("1800000"),
            "expected_ctc": Decimal("2800000"),
            "bio": "Passionate software craftsman with 5 years experience scaling B2B SaaS and payments products. Alumnus of BITS Pilani. Passionate about clean code, event-driven backends, and responsive React interfaces.",
            "linkedin_url": "https://linkedin.com/in/rohan-sharma-dev",
            "github_url": "https://github.com/rohan-sharma-bits",
            "skills": [("Python", "expert"), ("Django", "expert"), ("React.js", "intermediate"), ("PostgreSQL", "expert"), ("AWS", "intermediate")],
            "education": [
                {
                    "degree": "B.E. (Hons) in Computer Science",
                    "institution": "BITS Pilani",
                    "field_of_study": "Computer Science & Engineering",
                    "start_year": 2016,
                    "end_year": 2020,
                    "grade": "8.8 CGPA"
                }
            ],
            "experience": [
                {
                    "company_name": "Freshworks India",
                    "role_title": "Senior Software Engineer",
                    "start_date": "2022-04-01",
                    "end_date": "2026-10-01",
                    "is_current": True,
                    "description": "Scaled CRM messaging pipeline to handle 10,000 events/sec using Python, Redis, and PostgreSQL. Reduced query latencies by 42% through query index optimization."
                },
                {
                    "company_name": "Juspay Technologies",
                    "role_title": "Software Development Engineer 1",
                    "start_date": "2020-07-01",
                    "end_date": "2022-03-31",
                    "is_current": False,
                    "description": "Built core merchant checkout SDKs and integrated UPI payment flows for top e-commerce merchants in India."
                }
            ]
        },
        {
            "username": "ananya_design",
            "email": "ananya.iyer@example.com",
            "full_name": "Ananya Iyer",
            "headline": "Lead Product Designer | Dark-Mode Luxury & Consumer Apps",
            "location": "Mumbai, Maharashtra",
            "experience_years": 6,
            "current_ctc": Decimal("2200000"),
            "expected_ctc": Decimal("3500000"),
            "bio": "Design leader dedicated to crafting intuitive, emotionally resonant user experiences. Former Senior Designer at Hotstar & Cleartrip. Alumna of National Institute of Design (NID).",
            "linkedin_url": "https://linkedin.com/in/ananya-iyer-design",
            "github_url": "https://github.com/ananya-iyer",
            "skills": [("Figma", "expert"), ("UI/UX Prototyping", "expert"), ("Tailwind CSS", "beginner")],
            "education": [
                {
                    "degree": "Master of Design (M.Des)",
                    "institution": "National Institute of Design (NID), Ahmedabad",
                    "field_of_study": "Interaction & Digital Product Design",
                    "start_year": 2017,
                    "end_year": 2019,
                    "grade": "First Class with Distinction"
                }
            ],
            "experience": [
                {
                    "company_name": "Disney+ Hotstar India",
                    "role_title": "Senior Product Designer",
                    "start_date": "2022-01-01",
                    "end_date": "2026-09-01",
                    "is_current": True,
                    "description": "Redesigned the live sports streaming player for IPL tournament, resulting in a 18% lift in watch time engagement."
                }
            ]
        },
        {
            "username": "vikram_cloud",
            "email": "vikram.aditya@example.com",
            "full_name": "Vikram Aditya",
            "headline": "Staff DevOps & SRE Engineer | Kubernetes, Terraform & AWS",
            "location": "Hyderabad, Telangana",
            "experience_years": 7,
            "current_ctc": Decimal("2500000"),
            "expected_ctc": Decimal("3800000"),
            "bio": "SRE veteran passionate about 99.999% uptime, infrastructure as code, and observability. IIT Madras graduate.",
            "linkedin_url": "https://linkedin.com/in/vikram-aditya-cloud",
            "github_url": "https://github.com/vikram-aditya",
            "skills": [("Kubernetes", "expert"), ("AWS", "expert"), ("Docker", "expert"), ("Python", "intermediate")],
            "education": [
                {
                    "degree": "B.Tech in Electrical Engineering",
                    "institution": "IIT Madras",
                    "field_of_study": "Systems & Engineering",
                    "start_year": 2014,
                    "end_year": 2018,
                    "grade": "8.5 CGPA"
                }
            ],
            "experience": [
                {
                    "company_name": "Ola Cabs",
                    "role_title": "Senior Infrastructure Architect",
                    "start_date": "2021-08-01",
                    "end_date": "2026-10-01",
                    "is_current": True,
                    "description": "Maintained 400+ microservices on AWS EKS across Indian ride-hailing clusters."
                }
            ]
        }
    ]

    seeker_profiles = []
    for s_data in seekers_data:
        user, _ = User.objects.get_or_create(
            username=s_data["username"],
            defaults={
                "email": s_data["email"],
                "user_type": "jobseeker",
                "phone_number": "+91 99887 76655",
                "is_verified": True
            }
        )
        user.set_password("TestPass@123")
        user.save()

        profile, _ = JobSeekerProfile.objects.get_or_create(
            user=user,
            defaults={
                "full_name": s_data["full_name"],
                "headline": s_data["headline"],
                "location": s_data["location"],
                "experience_years": s_data["experience_years"],
                "current_ctc": s_data["current_ctc"],
                "expected_ctc": s_data["expected_ctc"],
                "bio": s_data["bio"],
                "linkedin_url": s_data["linkedin_url"],
                "github_url": s_data["github_url"],
                "is_open_to_work": True
            }
        )

        # Skills
        for sk_name, prof in s_data["skills"]:
            if sk_name in skills:
                JobSeekerSkill.objects.get_or_create(
                    jobseeker=profile,
                    skill=skills[sk_name],
                    defaults={"proficiency": prof}
                )

        # Education
        for edu in s_data["education"]:
            Education.objects.get_or_create(
                jobseeker=profile,
                degree=edu["degree"],
                institution=edu["institution"],
                defaults={
                    "field_of_study": edu["field_of_study"],
                    "start_year": edu["start_year"],
                    "end_year": edu["end_year"],
                    "grade": edu["grade"]
                }
            )

        # Experience
        for exp in s_data["experience"]:
            Experience.objects.get_or_create(
                jobseeker=profile,
                company_name=exp["company_name"],
                role_title=exp["role_title"],
                defaults={
                    "start_date": exp["start_date"],
                    "end_date": exp["end_date"],
                    "is_current": exp["is_current"],
                    "description": exp["description"]
                }
            )

        seeker_profiles.append(profile)

    print(f"[OK] Seeded {len(seeker_profiles)} realistic Indian candidate profiles with complete education & experience")

    # 6. Applications & Scheduled Interviews
    # Application 1: Rohan Sharma applies to Razorpay Lead Backend Architect
    job_razorpay = created_jobs[0]
    app1, _ = Application.objects.get_or_create(
        job=job_razorpay,
        applicant=seeker_profiles[0], # Rohan
        defaults={
            "cover_letter": "Hi Kavita and Razorpay team,\n\nI have spent the last 5 years scaling high-volume transactional backends using Python and PostgreSQL. Having built core payment rails at Juspay and Freshworks, I would love to contribute to Razorpay's mission-critical distributed gateway systems.\n\nLooking forward to discussing further.",
            "status": "interview_scheduled"
        }
    )
    ApplicationStatusHistory.objects.get_or_create(
        application=app1,
        new_status="interview_scheduled",
        defaults={
            "old_status": "under_review",
            "changed_by": employers[0].user,
            "notes": "Cleared technical screening. Scheduled system design interview round with Director of Engineering."
        }
    )
    # Interview for App 1
    Interview.objects.get_or_create(
        application=app1,
        defaults={
            "scheduled_at": timezone.now() + timedelta(days=2, hours=3),
            "mode": "virtual",
            "meeting_link": "https://meet.google.com/rzp-tech-arch",
            "interview_notes": "Technical Architecture & Distributed Systems Round with Lead Architect. Focus on Kafka & Postgres partitioning."
        }
    )

    # Application 2: Ananya Iyer applies to CRED Staff Product Designer
    job_cred = created_jobs[1]
    app2, _ = Application.objects.get_or_create(
        job=job_cred,
        applicant=seeker_profiles[1], # Ananya
        defaults={
            "cover_letter": "Hello Pooja and CRED Design team,\n\nCRED's visual depth, typography, and tactile delight has always inspired my craft. My experience leading live streaming interactions at Hotstar will bring valuable consumer immersion to CRED's design ecosystem.",
            "status": "interview_scheduled"
        }
    )
    Interview.objects.get_or_create(
        application=app2,
        defaults={
            "scheduled_at": timezone.now() + timedelta(days=3, hours=5),
            "mode": "virtual",
            "meeting_link": "https://meet.google.com/cred-design-portfolio",
            "interview_notes": "Portfolio Deep-dive & Visual Craft Review with Head of Design."
        }
    )

    # Application 3: Vikram Aditya applies to Razorpay Cloud Infrastructure
    job_infra = created_jobs[6]
    app3, _ = Application.objects.get_or_create(
        job=job_infra,
        applicant=seeker_profiles[2], # Vikram
        defaults={
            "cover_letter": "I have managed 400+ microservices on AWS EKS with Terraform at Ola. I would love to harden Razorpay's multi-region Kubernetes deployments.",
            "status": "under_review"
        }
    )
    ApplicationStatusHistory.objects.get_or_create(
        application=app3,
        new_status="under_review",
        defaults={
            "old_status": "applied",
            "changed_by": employers[0].user,
            "notes": "Portfolio under technical review by DevSecOps panel."
        }
    )

    # Bookmarked Jobs for Rohan
    SavedJob.objects.get_or_create(jobseeker=seeker_profiles[0], job=created_jobs[2]) # Zerodha
    SavedJob.objects.get_or_create(jobseeker=seeker_profiles[0], job=created_jobs[4]) # Postman

    print("[OK] Seeded realistic job applications, interview invitations, and saved bookmarks!")
    print("\n" + "="*70)
    print("SEEDING COMPLETE! READY TEST ACCOUNTS (Password for all: TestPass@123):")
    print("  - Job Seeker 1:  rohan_dev            (Senior Full Stack, BITS Pilani)")
    print("  - Job Seeker 2:  ananya_design        (Product Designer, NID)")
    print("  - Job Seeker 3:  vikram_cloud         (DevOps / SRE, IIT Madras)")
    print("  - Employer 1:    razorpay_recruiter   (Razorpay Software, Bengaluru)")
    print("  - Employer 2:    cred_hiring          (CRED, Bengaluru)")
    print("  - Employer 3:    zerodha_talent       (Zerodha Broking, Bengaluru)")
    print("="*70)

if __name__ == '__main__':
    seed()
