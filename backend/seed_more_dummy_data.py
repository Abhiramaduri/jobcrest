import os
import django
from datetime import datetime, timedelta, date
from decimal import Decimal
from django.utils import timezone
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, JobSeekerProfile, Skill, JobSeekerSkill, Education, Experience
from companies.models import Company, EmployerProfile
from jobs.models import JobCategory, Job, SavedJob
from applications.models import Application, ApplicationStatusHistory, Interview
from notifications.models import Notification

def get_unique_job_slug(title, company_name):
    base_slug = slugify(f"{title}-{company_name}")[:40].rstrip('-')
    slug = base_slug
    counter = 1
    while Job.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug

def get_unique_company_slug(name):
    base_slug = slugify(name)[:40].rstrip('-')
    slug = base_slug
    counter = 1
    while Company.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug

def run_seed():
    print("=" * 65)
    print("Starting Comprehensive Dummy Data Seeding for JobCrest...")
    print("=" * 65)

    # 1. Additional Skills
    extra_skills = [
        "Kubernetes", "Rust", "C++", "Terraform", "FastAPI", "React Native",
        "Flutter", "Snowflake", "dbt", "Tableau", "Power BI", "SEO & SEM",
        "Content Marketing", "B2B Sales", "SaaS Enterprise Sales",
        "Product Analytics", "A/B Testing", "Solidity", "Tailwind CSS",
        "CI/CD Pipelines", "Elasticsearch", "Apache Spark"
    ]
    skills_map = {}
    for s_name in extra_skills:
        sk, _ = Skill.objects.get_or_create(name=s_name)
        skills_map[s_name] = sk

    all_skills = {s.name: s for s in Skill.objects.all()}
    print(f"[OK] Total skills available: {len(all_skills)}")

    # 2. Categories
    categories = {cat.name: cat for cat in JobCategory.objects.all()}

    # 3. New Companies & Recruiters
    new_companies_data = [
        {
            "name": "Flipkart Internet",
            "industry": "E-Commerce & Retail",
            "company_size": "500+",
            "founded_year": 2007,
            "location": "Bengaluru, Karnataka",
            "website": "https://flipkart.com",
            "description": "Flipkart is India's leading e-commerce marketplace with a registered customer base of over 400 million, pioneering consumer internet in India.",
            "recruiter_username": "flipkart_recruiter",
            "recruiter_email": "talent@flipkart.com",
            "recruiter_first": "Arjun",
            "recruiter_last": "Kapoor",
            "designation": "Lead Tech Recruiter",
        },
        {
            "name": "PhonePe Technologies",
            "industry": "FinTech & Digital Payments",
            "company_size": "500+",
            "founded_year": 2015,
            "location": "Bengaluru, Karnataka",
            "website": "https://phonepe.com",
            "description": "PhonePe is India's leading digital payments platform with billions of monthly transactions across UPI, insurance, mutual funds, and wealth management.",
            "recruiter_username": "phonepe_recruiter",
            "recruiter_email": "hiring@phonepe.com",
            "recruiter_first": "Meera",
            "recruiter_last": "Nambiar",
            "designation": "Staff Talent Partner",
        },
        {
            "name": "Zomato Ltd",
            "industry": "FoodTech & Quick Commerce",
            "company_size": "500+",
            "founded_year": 2008,
            "location": "Gurugram, Haryana",
            "website": "https://zomato.com",
            "description": "Zomato connects millions of customers, delivery partners, and restaurant brands, transforming dining out and rapid grocery deliveries through Blinkit.",
            "recruiter_username": "zomato_recruiter",
            "recruiter_email": "talent@zomato.com",
            "recruiter_first": "Siddharth",
            "recruiter_last": "Bhatia",
            "designation": "Senior Technical Recruiter",
        },
        {
            "name": "Postman Software",
            "industry": "Developer Tools & API",
            "company_size": "500+",
            "founded_year": 2014,
            "location": "Bengaluru, Karnataka",
            "website": "https://postman.com",
            "description": "Postman is the leading collaboration platform for API development, used by over 30 million developers and 500,000 organizations globally.",
            "recruiter_username": "postman_recruiter",
            "recruiter_email": "careers@postman.com",
            "recruiter_first": "Divya",
            "recruiter_last": "Iyer",
            "designation": "Global Talent Acquisition Manager",
        },
        {
            "name": "Groww (Nextbillion Tech)",
            "industry": "WealthTech & Investments",
            "company_size": "201-500",
            "founded_year": 2016,
            "location": "Bengaluru, Karnataka",
            "website": "https://groww.in",
            "description": "Groww is a fast-growing financial services platform making investing in stocks, mutual funds, IPOs, and ETFs simple, transparent, and direct.",
            "recruiter_username": "groww_recruiter",
            "recruiter_email": "careers@groww.in",
            "recruiter_first": "Nikhil",
            "recruiter_last": "Agarwal",
            "designation": "Talent Partner - Engineering",
        },
        {
            "name": "Hasura India",
            "industry": "Cloud & Open Source",
            "company_size": "51-200",
            "founded_year": 2017,
            "location": "Bengaluru, Karnataka",
            "website": "https://hasura.io",
            "description": "Hasura makes data access blazingly fast and simple by providing instant GraphQL and REST APIs on PostgreSQL, MySQL, Snowflake, and more.",
            "recruiter_username": "hasura_recruiter",
            "recruiter_email": "hiring@hasura.io",
            "recruiter_first": "Shreya",
            "recruiter_last": "Ghoshal",
            "designation": "Principal Recruiter",
        },
        {
            "name": "Meesho E-Commerce",
            "industry": "Social Commerce & Marketplace",
            "company_size": "500+",
            "founded_year": 2015,
            "location": "Bengaluru, Karnataka",
            "website": "https://meesho.com",
            "description": "Meesho is building the single largest retail platform for next-billion Indian internet shoppers and small micro-entrepreneurs across tier 2/3 cities.",
            "recruiter_username": "meesho_recruiter",
            "recruiter_email": "jobs@meesho.com",
            "recruiter_first": "Vivek",
            "recruiter_last": "Nair",
            "designation": "Director of People",
        }
    ]

    company_objs = {}
    employer_objs = {}

    for c_data in new_companies_data:
        comp = Company.objects.filter(name=c_data["name"]).first()
        if not comp:
            comp_slug = get_unique_company_slug(c_data["name"])
            comp = Company.objects.create(
                name=c_data["name"],
                slug=comp_slug,
                industry=c_data["industry"],
                company_size=c_data["company_size"],
                founded_year=c_data["founded_year"],
                location=c_data["location"],
                website=c_data["website"],
                description=c_data["description"]
            )
        company_objs[c_data["name"]] = comp

        user = User.objects.filter(username=c_data["recruiter_username"]).first()
        if not user:
            user = User.objects.create_user(
                username=c_data["recruiter_username"],
                email=c_data["recruiter_email"],
                first_name=c_data["recruiter_first"],
                last_name=c_data["recruiter_last"],
                password="TestPass@123",
                user_type="employer",
                is_verified=True
            )
        emp_prof, _ = EmployerProfile.objects.get_or_create(
            user=user,
            defaults={
                "company": comp,
                "designation": c_data["designation"],
                "is_company_admin": True
            }
        )
        employer_objs[c_data["name"]] = emp_prof

    print(f"[OK] Seeded {len(new_companies_data)} top tech companies & hiring recruiters")

    # Fetch existing companies & employers for job distribution
    for c in Company.objects.all():
        company_objs[c.name] = c
        emp = EmployerProfile.objects.filter(company=c).first()
        if emp:
            employer_objs[c.name] = emp

    # 4. Rich Job Postings
    jobs_data = [
        {
            "company_name": "Flipkart Internet",
            "title": "Principal Distributed Systems Architect",
            "category_name": "Software Engineering",
            "job_type": "full-time",
            "location": "Bengaluru, Karnataka",
            "is_remote": False,
            "salary_min": Decimal("4500000.00"),
            "salary_max": Decimal("7500000.00"),
            "experience_min": 8,
            "experience_max": 14,
            "vacancies": 2,
            "description": "Flipkart's Core Platforms team is seeking an exceptional Principal Architect to design petabyte-scale distributed streaming, order fulfillment, and low-latency database sharding infrastructure handling Big Billion Days traffic surges.",
            "responsibilities": "- Lead technical vision, multi-datacenter resilience, and distributed transaction consistency across billions of events.\n- Architect high-throughput distributed caching, event broker clusters (Kafka), and NoSQL storage layers.\n- Mentor Principal Engineers and review high-impact design specifications across engineering orgs.",
            "requirements": "- 8+ years hands-on building massive scale distributed systems in Java/Go/Rust.\n- Deep mastery of Consensus algorithms (Raft, Paxos), Cassandra/RocksDB, and Kafka stream topologies.\n- Proven track record handling 50k+ QPS workloads in e-commerce or hyperscale cloud environments.",
            "skills": ["Java", "System Design", "Apache Kafka", "Docker", "Kubernetes", "Microservices Architecture"]
        },
        {
            "company_name": "PhonePe Technologies",
            "title": "Senior Backend Engineer - UPI Payments",
            "category_name": "Software Engineering",
            "job_type": "full-time",
            "location": "Bengaluru, Karnataka",
            "is_remote": False,
            "salary_min": Decimal("2800000.00"),
            "salary_max": Decimal("4800000.00"),
            "experience_min": 4,
            "experience_max": 8,
            "vacancies": 4,
            "description": "Join PhonePe's Core Payments team processing over 45% of all national UPI transaction volume. You will build mission-critical banking switch adapters and sub-10ms ledger settlement pipelines.",
            "responsibilities": "- Develop high-throughput microservices adhering to strict PCI-DSS & RBI banking specifications.\n- Optimize database query performance, lock contention, and idempotent payment dispatchers.\n- Collaborate with NPCI and bank integration partners for instant payment reconciliations.",
            "requirements": "- Strong background in Java or Go with multi-threaded concurrency experience.\n- In-depth understanding of distributed database ACID vs BASE, PostgreSQL tuning, and Redis caching patterns.\n- Familiarity with secure hashing, asymmetric encryption (RSA/ECC), and financial transaction auditing.",
            "skills": ["Java", "PostgreSQL", "Redis", "Microservices Architecture", "System Design"]
        },
        {
            "company_name": "Zomato Ltd",
            "title": "Lead Product Manager - Blinkit Rapid Commerce",
            "category_name": "Product Management",
            "job_type": "full-time",
            "location": "Gurugram, Haryana",
            "is_remote": False,
            "salary_min": Decimal("3200000.00"),
            "salary_max": Decimal("5500000.00"),
            "experience_min": 5,
            "experience_max": 9,
            "vacancies": 1,
            "description": "Own product roadmap for Blinkit 10-minute dark store supply chain, inventory prediction algorithms, and warehouse picking efficiency algorithms driving next-generation quick commerce across Indian metros.",
            "responsibilities": "- Define and drive features for dark store picker apps, predictive inventory replenishment, and ETA tracking.\n- Conduct data deep dives on order drop-offs, stock-out ratios, and customer retention metrics.\n- Collaborate closely with VP of Operations, Data Science, and Engineering leads.",
            "requirements": "- 5+ years product management experience at top B2C consumer internet, logistics, or foodtech startups.\n- High quantitative aptitude, SQL proficiency, and ability to translate ambiguity into crisp PRDs.\n- Strong customer obsession and first-principles operational mindset.",
            "skills": ["Product Analytics", "A/B Testing", "SQL", "System Design"]
        },
        {
            "company_name": "Postman Software",
            "title": "Senior Frontend Engineer - Developer Experience",
            "category_name": "Software Engineering",
            "job_type": "remote",
            "location": "Remote - India",
            "is_remote": True,
            "salary_min": Decimal("2600000.00"),
            "salary_max": Decimal("4200000.00"),
            "experience_min": 4,
            "experience_max": 7,
            "vacancies": 3,
            "description": "Postman is looking for a frontend specialist to craft fast, responsive, and delight-inducing developer tooling interfaces used daily by millions of API builders worldwide.",
            "responsibilities": "- Build complex browser and Electron desktop application components with React, TypeScript, and WebAssembly.\n- Maximize canvas rendering performance, syntax highlighting, and state management for large API schemas.\n- Advocate for web accessibility, UI design system consistency, and end-to-end Cypress test coverage.",
            "requirements": "- 4+ years of expert frontend development with modern React and TypeScript.\n- Deep knowledge of DOM lifecycle, performance profiling, WebSockets, and state management.\n- Contributions to open-source developer tooling is a significant plus.",
            "skills": ["React.js", "TypeScript", "Tailwind CSS", "Next.js", "GraphQL"]
        },
        {
            "company_name": "Groww (Nextbillion Tech)",
            "title": "Staff Site Reliability Engineer (Cloud & Infra)",
            "category_name": "Cloud & DevOps",
            "job_type": "full-time",
            "location": "Bengaluru, Karnataka",
            "is_remote": False,
            "salary_min": Decimal("3500000.00"),
            "salary_max": Decimal("6000000.00"),
            "experience_min": 6,
            "experience_max": 10,
            "vacancies": 2,
            "description": "Groww manages billions of rupees in equity trades daily. We are looking for a Staff SRE to elevate infrastructure resiliency, disaster recovery, zero-trust cloud architecture, and auto-scaling.",
            "responsibilities": "- Architect multi-region AWS and Kubernetes clusters with automated canary rollouts and circuit breakers.\n- Build self-healing infrastructure using Terraform, GitOps (ArgoCD), and Prometheus/Grafana alerting.\n- Lead Incident Command during production spikes and conduct blameless post-mortems.",
            "requirements": "- 6+ years hands-on SRE/DevOps experience managing high-uptime multi-tenant cloud architectures.\n- Deep mastery of Kubernetes internals, Envoy service mesh, Linux kernel tuning, and Terraform.\n- Fluency in Go or Python for automating infrastructure tooling.",
            "skills": ["Kubernetes", "Docker", "AWS", "Terraform", "CI/CD Pipelines", "Python"]
        },
        {
            "company_name": "Hasura India",
            "title": "Senior Solutions Engineer (Data APIs)",
            "category_name": "Sales & Strategic Partnerships",
            "job_type": "remote",
            "location": "Bengaluru, Karnataka / Remote",
            "is_remote": True,
            "salary_min": Decimal("2400000.00"),
            "salary_max": Decimal("4000000.00"),
            "experience_min": 3,
            "experience_max": 6,
            "vacancies": 2,
            "description": "Partner with Fortune 500 and high-growth enterprise engineering teams to design next-generation GraphQL data layers over modern enterprise data warehouses and microservices.",
            "responsibilities": "- Conduct architectural technical deep-dives and Proof-of-Concepts (PoCs) with Enterprise CTOs and architects.\n- Create reference implementations, whitepapers, and integration guides for GraphQL, PostgreSQL, and Snowflake.\n- Provide technical feedback from enterprise customers directly to Hasura product and engineering teams.",
            "requirements": "- 3+ years experience as a Solutions Architect, Technical Pre-Sales, or Full-Stack developer.\n- Excellent communication skills with strong knowledge of GraphQL, REST, and SQL databases.\n- Familiarity with enterprise authentication (OAuth2, SAML, JWT) and cloud platforms.",
            "skills": ["GraphQL", "PostgreSQL", "SQL", "Python", "B2B Sales"]
        },
        {
            "company_name": "Meesho E-Commerce",
            "title": "Staff Data Scientist - Recommendations & Search",
            "category_name": "Data Science & AI",
            "job_type": "full-time",
            "location": "Bengaluru, Karnataka",
            "is_remote": False,
            "salary_min": Decimal("3800000.00"),
            "salary_max": Decimal("6500000.00"),
            "experience_min": 5,
            "experience_max": 9,
            "vacancies": 2,
            "description": "Drive personalized discovery for 100M+ monthly active shoppers across vernacular languages. Build real-time neural recommendation models and multi-modal semantic search engines.",
            "responsibilities": "- Build two-tower neural recommendation models, graph neural networks (GNNs), and vector search indexing.\n- Optimize exploration vs exploitation algorithms and multi-objective ranking (CTR, CVR, Gross Margin).\n- Deploy low-latency online inference pipelines utilizing PyTorch, Triton, and Redis.",
            "requirements": "- 5+ years industry experience developing machine learning and ranking algorithms at e-commerce or social platforms.\n- Solid mathematical grounding in linear algebra, statistics, and deep learning architectures.\n- Strong programming skills in Python, PyTorch, Spark, and SQL.",
            "skills": ["Machine Learning", "PyTorch", "Python", "LLMs & GenAI", "SQL"]
        },
        {
            "company_name": "Razorpay Software",
            "title": "Lead Product Designer - Design Systems",
            "category_name": "UI/UX & Product Design",
            "job_type": "full-time",
            "location": "Bengaluru, Karnataka",
            "is_remote": False,
            "salary_min": Decimal("2500000.00"),
            "salary_max": Decimal("4200000.00"),
            "experience_min": 5,
            "experience_max": 8,
            "vacancies": 1,
            "description": "Evolve Blade — Razorpay's acclaimed open-source design system. You will craft accessible, tokenized UI components used across consumer checkout, payroll portals, and banking dashboards.",
            "responsibilities": "- Standardize interaction patterns, typography scales, tokens, and multi-brand component libraries in Figma.\n- Partner directly with frontend architects to ensure 100% parity between Figma and React Blade components.\n- Conduct usability testing and accessibility audits (WCAG 2.1 AA) across cross-functional product squads.",
            "requirements": "- 5+ years experience designing scalable design systems at leading tech companies or product studios.\n- Deep mastery of Figma (variants, component properties, auto-layout, design tokens).\n- Strong understanding of web fundamentals (HTML/CSS layout principles, responsive grids).",
            "skills": ["Figma", "UI/UX Prototyping", "Tailwind CSS"]
        },
        {
            "company_name": "CRED (Dreamplug Tech)",
            "title": "Security Engineering Specialist - Cloud & AppSec",
            "category_name": "Cloud & DevOps",
            "job_type": "full-time",
            "location": "Bengaluru, Karnataka",
            "is_remote": False,
            "salary_min": Decimal("3000000.00"),
            "salary_max": Decimal("5000000.00"),
            "experience_min": 4,
            "experience_max": 7,
            "vacancies": 1,
            "description": "CRED upholds highest security standards for India's premium cardholders. Build automated security scanning, secure vault enclave architectures, and bug bounty remediations.",
            "responsibilities": "- Implement automated SAST/DAST security gates inside GitHub Actions CI/CD pipelines.\n- Lead threat modeling sessions on new microservices, authentication handshakes, and cryptographic key stores.\n- Conduct internal red teaming and cloud security posture management (CSPM) across AWS infrastructure.",
            "requirements": "- 4+ years dedicated application security or cloud infrastructure security experience.\n- Familiarity with OWASP Top 10, container security (Kubernetes / Falco), and IAM least-privilege policies.\n- Industry certifications (OSCP, AWS Certified Security Specialty) are welcome.",
            "skills": ["AWS", "Docker", "Kubernetes", "CI/CD Pipelines", "Python"]
        },
        {
            "company_name": "Zerodha Broking",
            "title": "Systems Programmer (Golang & High-Frequency I/O)",
            "category_name": "Software Engineering",
            "job_type": "full-time",
            "location": "Bengaluru, Karnataka",
            "is_remote": False,
            "salary_min": Decimal("2800000.00"),
            "salary_max": Decimal("4800000.00"),
            "experience_min": 3,
            "experience_max": 6,
            "vacancies": 2,
            "description": "Zerodha's Kite platform executes over 15% of all Indian stock exchange trades. Work directly on Kite ticker feeds, binary protocol parsers, and low-latency order routing systems.",
            "responsibilities": "- Write idiomatic, allocation-free Go code capable of processing millions of market depth ticks per second.\n- Optimize TCP socket buffering, epoll concurrency, and IPC memory mapped ring buffers.\n- Benchmark and eliminate garbage collection pauses in latency-sensitive financial microservices.",
            "requirements": "- 3+ years experience writing performant Go, C, or Rust backend services.\n- Strong grasp of operating system fundamentals, CPU caching, and network protocols (WebSockets, TCP, UDP).\n- Genuine passion for open source software, simplicity, and frugal engineering.",
            "skills": ["Go (Golang)", "System Design", "PostgreSQL", "Redis", "Docker"]
        },
        {
            "company_name": "Swiggy Technologies",
            "title": "Growth Marketing & SEO Specialist",
            "category_name": "Marketing & Growth",
            "job_type": "full-time",
            "location": "Bengaluru, Karnataka",
            "is_remote": False,
            "salary_min": Decimal("1600000.00"),
            "salary_max": Decimal("2600000.00"),
            "experience_min": 3,
            "experience_max": 5,
            "vacancies": 2,
            "description": "Drive organic acquisition and organic app installs across 500+ Indian cities. Optimize local SEO landing pages, brand content marketing, and conversion funnels.",
            "responsibilities": "- Scale programmatic SEO landing pages for restaurants and hyper-local cuisines.\n- Coordinate with engineering to ensure peak Core Web Vitals and structured schema markup.\n- Run multi-channel keyword bidding and organic growth experiments.",
            "requirements": "- 3+ years demonstrable track record scaling SEO in high-growth B2C marketplaces.\n- Strong analytical fluency in Google Analytics 4, Search Console, and SQL data warehousing.",
            "skills": ["SEO & SEM", "Content Marketing", "Product Analytics", "SQL"]
        },
        {
            "company_name": "Hasura India",
            "title": "Technical Content & Developer Relations Engineer",
            "category_name": "Marketing & Growth",
            "job_type": "remote",
            "location": "Remote - India",
            "is_remote": True,
            "salary_min": Decimal("1800000.00"),
            "salary_max": Decimal("3000000.00"),
            "experience_min": 2,
            "experience_max": 5,
            "vacancies": 1,
            "description": "Create world-class technical tutorials, architectural sample repos, and video walkthroughs teaching developers how to harness instant GraphQL on SQL databases.",
            "responsibilities": "- Author in-depth technical blogs, sample full-stack boilerplate apps (Next.js + Hasura + PostgreSQL).\n- Speak at developer conferences, host community meetups, and answer technical questions on Discord/GitHub.\n- Partner with product engineering to beta test upcoming features and SDKs.",
            "requirements": "- 2+ years experience in developer relations, technical writing, or software engineering.\n- Ability to write clean, working code in TypeScript, React, and Python.\n- Excellent English writing skills and a knack for explaining complex technical topics clearly.",
            "skills": ["GraphQL", "React.js", "PostgreSQL", "Content Marketing"]
        }
    ]

    seeded_jobs = []
    for jd in jobs_data:
        comp = company_objs.get(jd["company_name"])
        if not comp:
            continue
        emp = employer_objs.get(jd["company_name"])
        cat = categories.get(jd["category_name"])

        # Check if job already exists
        job = Job.objects.filter(title=jd["title"], company=comp).first()
        if not job:
            unique_slug = get_unique_job_slug(jd["title"], comp.name)
            job = Job.objects.create(
                title=jd["title"],
                slug=unique_slug,
                company=comp,
                posted_by=emp,
                category=cat,
                description=jd["description"],
                responsibilities=jd["responsibilities"],
                requirements=jd["requirements"],
                job_type=jd["job_type"],
                experience_min=jd["experience_min"],
                experience_max=jd["experience_max"],
                salary_min=jd["salary_min"],
                salary_max=jd["salary_max"],
                salary_currency="INR",
                location=jd["location"],
                is_remote=jd["is_remote"],
                vacancies=jd["vacancies"],
                status="published",
                application_deadline=date.today() + timedelta(days=45),
                views_count=120
            )
            # Add skills
            for sk_name in jd["skills"]:
                if sk_name in all_skills:
                    job.skill_required.add(all_skills[sk_name])
            seeded_jobs.append(job)
        else:
            seeded_jobs.append(job)

    print(f"[OK] Successfully verified/seeded {len(seeded_jobs)} rich job openings")

    # 5. More Diverse Candidates
    candidates_data = [
        {
            "username": "priya_fullstack",
            "email": "priya.sharma@example.com",
            "first_name": "Priya",
            "last_name": "Sharma",
            "headline": "Lead Full Stack Engineer | Python, React, AWS | Ex-Swiggy",
            "bio": "Experienced Full Stack engineer with 6+ years building scalable fintech and e-commerce applications. Passionate about clean code, high concurrency, and intuitive UI.",
            "location": "Bengaluru, Karnataka",
            "experience_years": 6,
            "current_ctc": Decimal("2400000.00"),
            "expected_ctc": Decimal("3200000.00"),
            "skills": [("Python", "expert"), ("Django", "expert"), ("React.js", "expert"), ("PostgreSQL", "intermediate"), ("AWS", "intermediate")],
            "education": {
                "degree": "B.Tech in Computer Science",
                "institution": "National Institute of Technology (NIT) Trichy",
                "field_of_study": "Computer Science & Engineering",
                "start_year": 2014,
                "end_year": 2018,
                "grade": "8.8 CGPA"
            },
            "experience": {
                "company_name": "Swiggy Technologies",
                "role_title": "Senior Software Engineer",
                "start_date": date(2021, 6, 1),
                "is_current": True,
                "description": "Architected partner portal microservices handling over 500k daily merchant interactions. Reduced latency by 35% through Redis caching."
            }
        },
        {
            "username": "karthik_ai",
            "email": "karthik.ram@example.com",
            "first_name": "Karthik",
            "last_name": "Ramaswamy",
            "headline": "Machine Learning Engineer & GenAI Specialist | PyTorch, LLMs",
            "bio": "ML practitioner focused on fine-tuning open-source LLMs, vector search, and recommender systems. Published researcher with 4 years in applied AI.",
            "location": "Hyderabad, Telangana",
            "experience_years": 4,
            "current_ctc": Decimal("1900000.00"),
            "expected_ctc": Decimal("2800000.00"),
            "skills": [("Machine Learning", "expert"), ("PyTorch", "expert"), ("LLMs & GenAI", "expert"), ("Python", "expert"), ("SQL", "intermediate")],
            "education": {
                "degree": "M.Tech in Artificial Intelligence",
                "institution": "IIT Hyderabad",
                "field_of_study": "Machine Learning & AI",
                "start_year": 2018,
                "end_year": 2020,
                "grade": "9.2 CGPA"
            },
            "experience": {
                "company_name": "InMobi",
                "role_title": "Data Scientist II",
                "start_date": date(2020, 7, 15),
                "is_current": True,
                "description": "Engineered real-time click-through-rate prediction models processing 200M+ ad impressions daily using PyTorch and Triton server."
            }
        },
        {
            "username": "tanvi_product",
            "email": "tanvi.verma@example.com",
            "first_name": "Tanvi",
            "last_name": "Verma",
            "headline": "Senior Product Manager | FinTech & Growth | IIM Ahmedabad Alum",
            "bio": "Results-driven Product Manager with expertise in 0-to-1 product launches, regulatory compliance in banking, and data-driven user activation funnels.",
            "location": "Mumbai, Maharashtra",
            "experience_years": 5,
            "current_ctc": Decimal("2600000.00"),
            "expected_ctc": Decimal("3600000.00"),
            "skills": [("Product Analytics", "expert"), ("A/B Testing", "expert"), ("SQL", "intermediate"), ("System Design", "intermediate")],
            "education": {
                "degree": "MBA in General Management",
                "institution": "IIM Ahmedabad",
                "field_of_study": "Business & Strategy",
                "start_year": 2017,
                "end_year": 2019,
                "grade": "Dean's Honor List"
            },
            "experience": {
                "company_name": "Paytm",
                "role_title": "Product Manager - Lending",
                "start_date": date(2019, 6, 1),
                "is_current": True,
                "description": "Scaled digital merchant loan origination from zero to ₹150Cr monthly disbursement volume through seamless KYC and paperless underwriting."
            }
        }
    ]

    candidate_profiles = []
    for cand in candidates_data:
        u = User.objects.filter(username=cand["username"]).first()
        if not u:
            u = User.objects.create_user(
                username=cand["username"],
                email=cand["email"],
                first_name=cand["first_name"],
                last_name=cand["last_name"],
                password="TestPass@123",
                user_type="jobseeker",
                is_verified=True
            )
        prof, _ = JobSeekerProfile.objects.get_or_create(
            user=u,
            defaults={
                "full_name": f"{cand['first_name']} {cand['last_name']}",
                "headline": cand["headline"],
                "bio": cand["bio"],
                "location": cand["location"],
                "experience_years": cand["experience_years"],
                "current_ctc": cand["current_ctc"],
                "expected_ctc": cand["expected_ctc"],
                "is_open_to_work": True
            }
        )
        # Skills
        for sk_name, prof_level in cand["skills"]:
            if sk_name in all_skills:
                JobSeekerSkill.objects.get_or_create(
                    jobseeker=prof,
                    skill=all_skills[sk_name],
                    defaults={"proficiency": prof_level}
                )
        # Education
        edu_d = cand["education"]
        Education.objects.get_or_create(
            jobseeker=prof,
            degree=edu_d["degree"],
            institution=edu_d["institution"],
            defaults={
                "field_of_study": edu_d["field_of_study"],
                "start_year": edu_d["start_year"],
                "end_year": edu_d["end_year"],
                "grade": edu_d["grade"]
            }
        )
        # Experience
        exp_d = cand["experience"]
        Experience.objects.get_or_create(
            jobseeker=prof,
            company_name=exp_d["company_name"],
            role_title=exp_d["role_title"],
            defaults={
                "start_date": exp_d["start_date"],
                "is_current": exp_d["is_current"],
                "description": exp_d["description"]
            }
        )
        candidate_profiles.append(prof)

    print(f"[OK] Seeded {len(candidate_profiles)} new verified candidate profiles with education, skills & work experience")

    # Add existing job seekers to candidate_profiles list for applications & bookmarks
    for jsp in JobSeekerProfile.objects.all():
        if jsp not in candidate_profiles:
            candidate_profiles.append(jsp)

    # 6. Applications, Interviews & Bookmarks
    all_published_jobs = list(Job.objects.filter(status="published"))
    app_scenarios = [
        ("under_review", "Your application is currently being evaluated by the hiring committee."),
        ("shortlisted", "Congratulations! Your profile has been shortlisted for further technical rounds."),
        ("interview_scheduled", "Your virtual interview with the Engineering Manager has been scheduled."),
        ("hired", "Congratulations! We are thrilled to offer you this position."),
        ("rejected", "Thank you for your interest. While impressive, we decided to move forward with other candidates at this time.")
    ]

    apps_created = 0
    interviews_created = 0
    saved_created = 0

    for idx, candidate in enumerate(candidate_profiles):
        # Save 2-3 jobs as bookmarks
        for job_to_save in all_published_jobs[idx : idx + 3]:
            _, created = SavedJob.objects.get_or_create(jobseeker=candidate, job=job_to_save)
            if created:
                saved_created += 1

        # Submit applications to 2 jobs
        for job_idx, target_job in enumerate(all_published_jobs[(idx * 2) : (idx * 2) + 2]):
            app, created = Application.objects.get_or_create(
                job=target_job,
                applicant=candidate,
                defaults={
                    "cover_letter": f"Dear Hiring Team at {target_job.company.name},\n\nI am thrilled to apply for the {target_job.title} role. With my background in {candidate.headline}, I am confident in delivering high impact.\n\nBest regards,\n{candidate.full_name}",
                    "status": "applied"
                }
            )
            if created:
                apps_created += 1
                status_choice, status_note = app_scenarios[(idx + job_idx) % len(app_scenarios)]
                app.status = status_choice
                app.save()

                # Status history
                ApplicationStatusHistory.objects.create(
                    application=app,
                    old_status="applied",
                    new_status=status_choice,
                    changed_by=target_job.posted_by.user if target_job.posted_by else None,
                    notes=status_note
                )

                # If interview scheduled, create interview entry
                if status_choice == "interview_scheduled":
                    interview_time = timezone.now() + timedelta(days=3, hours=2)
                    Interview.objects.create(
                        application=app,
                        scheduled_at=interview_time,
                        mode="virtual",
                        meeting_link="https://meet.google.com/job-crst-demo",
                        interview_notes="45-minute technical system design & past experience deep dive.",
                        result="pending"
                    )
                    interviews_created += 1

                # Send in-app notification to candidate
                Notification.objects.create(
                    user=candidate.user,
                    title=f"Application Update: {target_job.title}",
                    message=f"Your application at {target_job.company.name} has been updated to: {app.get_status_display()}.",
                    notification_type="interview_scheduled" if status_choice == "interview_scheduled" else "application_update"
                )

    print(f"[OK] Seeded {apps_created} new applications with complete audit history")
    print(f"[OK] Seeded {interviews_created} scheduled technical interviews with meeting links")
    print(f"[OK] Seeded {saved_created} job bookmarks for active candidates")

    # 7. Add sample general & match notifications
    for cand in candidate_profiles:
        Notification.objects.create(
            user=cand.user,
            title="New Jobs Matching Your Profile",
            message="We found 4 new high-priority openings matching your technical skill set. Check your recommendations!",
            notification_type="new_job_match"
        )

    print(f"[OK] Generated system notifications for all active candidates")

    # Print summary
    print("\n" + "=" * 65)
    print("DUMMY DATA SEEDING COMPLETE!")
    print(f"Total Users:        {User.objects.count()}")
    print(f"Total Companies:    {Company.objects.count()}")
    print(f"Total Jobs:         {Job.objects.count()}")
    print(f"Total Applications: {Application.objects.count()}")
    print(f"Total Interviews:   {Interview.objects.count()}")
    print(f"Total Saved Jobs:   {SavedJob.objects.count()}")
    print("=" * 65)
    print("NEW READY TEST ACCOUNTS (Password: TestPass@123):")
    print("  - Candidate:  priya_fullstack   (Lead Full Stack, Ex-Swiggy)")
    print("  - Candidate:  karthik_ai        (ML Engineer / GenAI, IIT Hyderabad)")
    print("  - Candidate:  tanvi_product     (Senior PM, IIM Ahmedabad)")
    print("  - Recruiter:  flipkart_recruiter")
    print("  - Recruiter:  phonepe_recruiter")
    print("  - Recruiter:  postman_recruiter")
    print("  - Recruiter:  zomato_recruiter")
    print("=" * 65)

if __name__ == "__main__":
    run_seed()

