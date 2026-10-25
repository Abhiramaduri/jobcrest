#!/usr/bin/env python3
"""
JobCrest API Test Runner
========================
This script executes end-to-end API tests across all endpoints in the JobCrest project:
  - Auth & JWT lifecycle (Register, Login, Token Refresh, Me, Reset, Logout)
  - JobSeeker Profile, Education, Experience & Skills
  - Company & Employer Management
  - Jobs, Search, Filtering, Recommendations & Saved Jobs
  - Applications, Status History & Interviews

Usage:
  python run_api_tests.py
  python run_api_tests.py --base-url http://127.0.0.1:8000/api
  python run_api_tests.py --error-file api_errors.log

If any error occurs, it writes a detailed error report to `api_errors.log`.
"""

import sys
import os
import json
import time
import argparse
import subprocess
from datetime import datetime
import urllib.request
import urllib.error

# Ensure stdout handles UTF-8 on Windows consoles safely
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Configurable defaults
DEFAULT_BASE_URL = "http://127.0.0.1:8000/api"
DEFAULT_ERROR_FILE = "api_errors.log"


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


class ApiTestRunner:
    def __init__(self, base_url=DEFAULT_BASE_URL, error_file=DEFAULT_ERROR_FILE):
        self.base_url = base_url.rstrip("/")
        self.error_file = error_file
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []
        
        # Runtime session state
        self.jobseeker_token = None
        self.jobseeker_refresh = None
        self.employer_token = None
        self.employer_refresh = None
        self.created_company_slug = None
        self.created_job_slug = None
        self.created_job_id = None
        self.created_app_id = None
        self.created_interview_id = None
        self.created_edu_id = None
        self.created_exp_id = None
        self.created_skill_id = None
        self.created_js_skill_id = None
        self.jobseeker_profile_id = None
        self.employer_user_id = None
        self.jobseeker_user_id = None

    def request(self, method, endpoint, payload=None, token=None, expected_status=None):
        """Sends an HTTP request and logs errors if status doesn't match expected_status."""
        self.tests_run += 1
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Accept": "application/json",
            "User-Agent": "JobCrest-ApiTestRunner/1.0"
        }
        
        body_bytes = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body_bytes = json.dumps(payload).encode("utf-8")
            
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method.upper())
        start_time = time.time()
        
        status_code = None
        response_data = None
        raw_response_text = ""
        error_msg = None
        
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                status_code = resp.status
                raw_response_text = resp.read().decode("utf-8")
                if raw_response_text:
                    try:
                        response_data = json.loads(raw_response_text)
                    except Exception:
                        response_data = raw_response_text
        except urllib.error.HTTPError as e:
            status_code = e.code
            try:
                raw_response_text = e.read().decode("utf-8")
                response_data = json.loads(raw_response_text)
            except Exception:
                response_data = raw_response_text
        except Exception as e:
            error_msg = str(e)
            
        duration = round((time.time() - start_time) * 1000, 2)
        
        # Determine pass / fail
        is_expected = False
        if expected_status is not None:
            if isinstance(expected_status, (list, tuple, set)):
                is_expected = status_code in expected_status
            else:
                is_expected = (status_code == expected_status)
        else:
            is_expected = (status_code is not None and 200 <= status_code < 400)
            
        if is_expected and not error_msg:
            self.tests_passed += 1
            print(f"  {Colors.GREEN}[PASS]{Colors.RESET} {method:<6} {endpoint:<45} Status: {status_code} ({duration}ms)")
            return True, response_data, status_code
        else:
            fail_reason = error_msg if error_msg else f"Expected status {expected_status}, got {status_code}"
            print(f"  {Colors.RED}[FAIL]{Colors.RESET} {method:<6} {endpoint:<45} Status: {status_code} ({duration}ms) - {fail_reason}")
            self.errors.append({
                "test_number": self.tests_run,
                "timestamp": datetime.now().isoformat(),
                "method": method.upper(),
                "url": url,
                "endpoint": endpoint,
                "request_headers": headers,
                "request_payload": payload,
                "expected_status": expected_status,
                "actual_status": status_code,
                "error_reason": fail_reason,
                "response_body": response_data or raw_response_text
            })
            return False, response_data, status_code

    def check_server(self):
        """Verifies if the Django server is accessible."""
        try:
            req = urllib.request.Request(self.base_url + "/skills/", headers={"User-Agent": "JobCrest-Runner"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                return True
        except urllib.error.HTTPError as e:
            return True
        except Exception:
            return False

    def setup_seed_data(self):
        """Ensures at least one Skill and JobCategory exist for test dependencies."""
        try:
            setup_script = (
                "import os, django; "
                "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); "
                "django.setup(); "
                "from accounts.models import Skill; "
                "from jobs.models import JobCategory; "
                "Skill.objects.get_or_create(name='Python'); "
                "Skill.objects.get_or_create(name='Django'); "
                "JobCategory.objects.get_or_create(name='Software Engineering'); "
            )
            subprocess.run([sys.executable, "-c", setup_script], check=True, capture_output=True)
        except Exception as e:
            pass

    def run_all(self):
        start_wall_time = datetime.now()
        ts = int(time.time())
        js_username = f"seeker_{ts}"
        emp_username = f"emp_{ts}"
        
        print(f"{Colors.BOLD}{'='*80}")
        print(f" JOBCREST REST API TEST SUITE")
        print(f" Target Base URL: {self.base_url}")
        print(f" Started At: {start_wall_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}{Colors.RESET}\n")

        # -------------------------------------------------------------
        # 1. AUTHENTICATION & USER MANAGEMENT
        # -------------------------------------------------------------
        print(f"{Colors.BOLD}[1] Authentication & Token Lifecycle{Colors.RESET}")
        
        # 1.1 Register JobSeeker
        ok, data, _ = self.request("POST", "/auth/register/", {
            "username": js_username,
            "email": f"{js_username}@example.com",
            "password": "Password123!",
            "password2": "Password123!",
            "user_type": "jobseeker",
            "phone_number": "9876543210"
        }, expected_status=201)
        if ok and data and "access" in data:
            self.jobseeker_token = data.get("access")
            self.jobseeker_refresh = data.get("refresh")
            if "user" in data and isinstance(data["user"], dict):
                self.jobseeker_user_id = data["user"].get("id")

        # 1.2 Register Employer
        ok, data, _ = self.request("POST", "/auth/register/", {
            "username": emp_username,
            "email": f"{emp_username}@example.com",
            "password": "Password123!",
            "password2": "Password123!",
            "user_type": "employer",
            "phone_number": "9123456780"
        }, expected_status=201)
        if ok and data and "access" in data:
            self.employer_token = data.get("access")
            self.employer_refresh = data.get("refresh")
            if "user" in data and isinstance(data["user"], dict):
                self.employer_user_id = data["user"].get("id")

        # 1.3 Login JobSeeker
        ok, data, _ = self.request("POST", "/auth/login/", {
            "username": js_username,
            "password": "Password123!"
        }, expected_status=200)
        if ok and data:
            self.jobseeker_token = data.get("access")
            self.jobseeker_refresh = data.get("refresh")

        # 1.4 Login Employer
        ok, data, _ = self.request("POST", "/auth/login/", {
            "username": emp_username,
            "password": "Password123!"
        }, expected_status=200)
        if ok and data:
            self.employer_token = data.get("access")
            self.employer_refresh = data.get("refresh")

        # 1.5 Refresh Access Token
        if self.jobseeker_refresh:
            ok, data, _ = self.request("POST", "/auth/refresh/", {
                "refresh": self.jobseeker_refresh
            }, expected_status=200)
            if ok and data and "access" in data:
                self.jobseeker_token = data.get("access")

        # 1.6 Me View (Authenticated)
        self.request("GET", "/auth/me", token=self.jobseeker_token, expected_status=200)

        # 1.7 Password Reset Request
        self.request("POST", "/auth/password-reset/", {
            "email": f"{js_username}@example.com"
        }, expected_status=200)

        # 1.8 Password Reset Confirm
        self.request("POST", "/auth/password-reset-confirm/", {
            "new_password": "NewStrongPassword123!"
        }, expected_status=200)

        # -------------------------------------------------------------
        # 2. JOBSEEKER PROFILE, EDUCATION, EXPERIENCE & SKILLS
        # -------------------------------------------------------------
        print(f"\n{Colors.BOLD}[2] JobSeeker Profile, Education, Experience & Skills{Colors.RESET}")
        
        # 2.1 Get All Public Skills
        ok, data, _ = self.request("GET", "/skills/", expected_status=200)
        if ok and isinstance(data, list) and len(data) > 0:
            self.created_skill_id = data[0].get("id")

        # 2.2 Get JobSeeker Profile
        ok, data, _ = self.request("GET", "/jobseeker/profile/", token=self.jobseeker_token, expected_status=200)
        if ok and data:
            self.jobseeker_profile_id = data.get("id")

        # 2.3 Update JobSeeker Profile (PUT)
        self.request("PUT", "/jobseeker/profile/", {
            "full_name": "Demo JobSeeker Candidate",
            "headline": "Senior Full Stack Python Engineer",
            "bio": "Specialized in scalable distributed backends and Django APIs.",
            "date_of_birth": "1998-05-20",
            "location": "Bangalore, India",
            "experience_years": 4,
            "current_ctc": "900000.00",
            "expected_ctc": "1500000.00",
            "linkedin_url": "https://linkedin.com/in/demo-candidate",
            "github_url": "https://github.com/demo-candidate",
            "is_open_to_work": True
        }, token=self.jobseeker_token, expected_status=200)

        # 2.4 Partial Update JobSeeker Profile (PATCH)
        self.request("PATCH", "/jobseeker/profile/", {
            "headline": "Lead Python/Django Systems Architect",
            "location": "Remote / Hyderabad"
        }, token=self.jobseeker_token, expected_status=200)

        # 2.5 Public Profile
        if self.jobseeker_profile_id:
            self.request("GET", f"/jobseeker/profile/{self.jobseeker_profile_id}", token=self.jobseeker_token, expected_status=200)

        # 2.6 Add Education
        ok, data, _ = self.request("POST", "/jobseeker/education/", {
            "degree": "B.Tech Computer Science",
            "institution": "National Institute of Technology",
            "field_of_study": "Computer Science & Engineering",
            "start_year": 2018,
            "end_year": 2022,
            "grade": "8.8 CGPA"
        }, token=self.jobseeker_token, expected_status=201)
        if ok and data:
            self.created_edu_id = data.get("id")

        # 2.7 List Education
        self.request("GET", "/jobseeker/education/", token=self.jobseeker_token, expected_status=200)

        # 2.8 Education Detail & Update
        if self.created_edu_id:
            self.request("GET", f"/jobseeker/education/{self.created_edu_id}/", token=self.jobseeker_token, expected_status=200)
            self.request("PATCH", f"/jobseeker/education/{self.created_edu_id}/", {"grade": "9.0 CGPA"}, token=self.jobseeker_token, expected_status=200)

        # 2.9 Add Experience
        ok, data, _ = self.request("POST", "/jobseeker/experience/", {
            "company_name": "CloudTech Labs",
            "role_title": "Backend Software Engineer",
            "start_date": "2022-08-01",
            "is_current": True,
            "description": "Designed microservices, built REST APIs and tuned database queries."
        }, token=self.jobseeker_token, expected_status=201)
        if ok and data:
            self.created_exp_id = data.get("id")

        # 2.10 List Experience
        self.request("GET", "/jobseeker/experience/", token=self.jobseeker_token, expected_status=200)

        # 2.11 Experience Detail & Update
        if self.created_exp_id:
            self.request("GET", f"/jobseeker/experience/{self.created_exp_id}/", token=self.jobseeker_token, expected_status=200)
            self.request("PATCH", f"/jobseeker/experience/{self.created_exp_id}/", {"role_title": "Senior Backend Software Engineer"}, token=self.jobseeker_token, expected_status=200)

        # 2.12 Add Skill to Profile
        if self.created_skill_id:
            ok, data, _ = self.request("POST", "/jobseeker/skills/", {
                "skill": self.created_skill_id,
                "proficiency": "expert"
            }, token=self.jobseeker_token, expected_status=201)
            if ok and data:
                self.created_js_skill_id = data.get("id")

        # 2.13 List JobSeeker Skills
        self.request("GET", "/jobseeker/skills/", token=self.jobseeker_token, expected_status=200)

        # -------------------------------------------------------------
        # 3. COMPANIES & EMPLOYER MANAGEMENT
        # -------------------------------------------------------------
        print(f"\n{Colors.BOLD}[3] Companies & Employer Profile Management{Colors.RESET}")
        
        # 3.1 List Companies (Public)
        self.request("GET", "/companies/", expected_status=200)

        # 3.2 Create Company (Employer)
        comp_name = f"Enterprise Apex {ts}"
        ok, data, _ = self.request("POST", "/companies/", {
            "name": comp_name,
            "industry": "Information Technology & Software",
            "location": "Bangalore, India",
            "company_size": "51-200",
            "website": "https://enterprise-apex.example.com",
            "description": "Leading innovator in enterprise cloud software and automated API services.",
            "founded_year": 2021
        }, token=self.employer_token, expected_status=201)
        if ok and data:
            self.created_company_slug = data.get("slug")

        # 3.3 Get Company Detail & Update
        if self.created_company_slug:
            self.request("GET", f"/companies/{self.created_company_slug}/", expected_status=200)
            self.request("PATCH", f"/companies/{self.created_company_slug}/", {
                "description": "Global developer of cloud, mobile, and AI solutions.",
                "company_size": "201-500"
            }, token=self.employer_token, expected_status=200)
            self.request("GET", f"/companies/{self.created_company_slug}/recruiters/", token=self.employer_token, expected_status=200)

        # 3.4 Employer Profile View
        self.request("GET", "/employers/profile/", token=self.employer_token, expected_status=200)
        self.request("PATCH", "/employers/profile/", {
            "designation": "Director of Technical Talent"
        }, token=self.employer_token, expected_status=200)

        # -------------------------------------------------------------
        # 4. JOBS
        # -------------------------------------------------------------
        print(f"\n{Colors.BOLD}[4] Jobs Postings, Search & Saved Jobs{Colors.RESET}")
        
        # 4.1 Job Categories & Reference Skills
        ok, cat_data, _ = self.request("GET", "/jobs/categories/", expected_status=200)
        cat_id = cat_data[0].get("id") if (ok and cat_data and len(cat_data) > 0) else 1
        self.request("GET", "/jobs/skills/", expected_status=200)

        # 4.2 Create Job Posting (Employer)
        job_title = f"Backend Lead {ts % 10000}"
        ok, data, _ = self.request("POST", "/jobs/", {
            "title": job_title,
            "category": cat_id,
            "description": "We are looking for a Senior Python Engineer to manage high-throughput Django systems.",
            "responsibilities": "Write unit tests, create endpoints, configure database indexes, and review code.",
            "requirements": "3+ years Python, PostgreSQL, Django REST Framework.",
            "job_type": "full-time",
            "experience_min": 3,
            "experience_max": 7,
            "salary_min": "1400000.00",
            "salary_max": "2200000.00",
            "salary_currency": "INR",
            "location": "Bangalore, India",
            "is_remote": True,
            "skills_required": [self.created_skill_id] if self.created_skill_id else [],
            "vacancies": 3,
            "status": "published",
            "application_deadline": "2026-12-31"
        }, token=self.employer_token, expected_status=201)
        if ok and data:
            self.created_job_slug = data.get("slug")
            self.created_job_id = data.get("id")

        # 4.3 List Published Jobs with Search & Filters
        self.request("GET", "/jobs/?search=python&ordering=-created_at", expected_status=200)

        # 4.4 Job Detail View
        if self.created_job_slug:
            self.request("GET", f"/jobs/{self.created_job_slug}/", expected_status=200)
            self.request("PATCH", f"/jobs/{self.created_job_slug}/", {
                "vacancies": 5
            }, token=self.employer_token, expected_status=200)
            self.request("PATCH", f"/jobs/{self.created_job_slug}/status/", {
                "status": "published"
            }, token=self.employer_token, expected_status=200)

        # 4.5 Employer My Postings
        self.request("GET", "/jobs/my-postings/", token=self.employer_token, expected_status=200)

        # 4.6 Recommended Jobs
        self.request("GET", "/jobs/recommended/", token=self.jobseeker_token, expected_status=200)

        # 4.7 Save Job
        if self.created_job_slug:
            self.request("POST", f"/jobs/{self.created_job_slug}/save/", token=self.jobseeker_token, expected_status=201)
            self.request("GET", "/jobs/saved/", token=self.jobseeker_token, expected_status=200)
            self.request("DELETE", f"/jobs/{self.created_job_slug}/unsave/", token=self.jobseeker_token, expected_status=204)

        # -------------------------------------------------------------
        # 5. APPLICATIONS & INTERVIEWS
        # -------------------------------------------------------------
        print(f"\n{Colors.BOLD}[5] Applications & Interview Scheduling{Colors.RESET}")
        
        # 5.1 Apply to Job
        if self.created_job_id:
            ok, data, _ = self.request("POST", "/application/", {
                "job": self.created_job_id,
                "cover_letter": "I have extensive experience building scalable APIs in Django and DRF."
            }, token=self.jobseeker_token, expected_status=201)
            if ok and data:
                self.created_app_id = data.get("id")

        # 5.2 List Jobseeker Applications
        self.request("GET", "/applications/my-application/", token=self.jobseeker_token, expected_status=200)

        # 5.3 Employer View Applications for this Job
        if self.created_job_id:
            self.request("GET", f"/applications/job/{self.created_job_id}/", token=self.employer_token, expected_status=200)

        # 5.4 Application Detail View
        if self.created_app_id:
            self.request("GET", f"/applications/{self.created_app_id}/", token=self.jobseeker_token, expected_status=200)
            
            # 5.5 Update Application Status (Employer)
            self.request("PATCH", f"/applications/{self.created_app_id}/status/", {
                "status": "shortlisted",
                "notes": "Candidate matches backend profile requirements."
            }, token=self.employer_token, expected_status=200)

            # 5.6 Status History
            self.request("GET", f"/applications/{self.created_app_id}/history/", token=self.jobseeker_token, expected_status=200)

            # 5.7 Schedule Interview (Employer)
            ok, data, _ = self.request("POST", "/interviews/", {
                "application": self.created_app_id,
                "scheduled_at": "2026-11-20T10:00:00Z",
                "mode": "online",
                "meeting_link": "https://meet.google.com/test-room-123",
                "interview_notes": "Round 1: System Design and Django API Architecture."
            }, token=self.employer_token, expected_status=201)
            if ok and data:
                self.created_interview_id = data.get("id")

        # 5.8 List Interviews
        self.request("GET", "/interviews/my-interviews/", token=self.jobseeker_token, expected_status=200)
        self.request("GET", "/interviews/employer/", token=self.employer_token, expected_status=200)

        # 5.9 Interview Detail & Update
        if self.created_interview_id:
            self.request("GET", f"/interviews/{self.created_interview_id}/", token=self.jobseeker_token, expected_status=200)
            self.request("PATCH", f"/interviews/{self.created_interview_id}/", {
                "result": "passed",
                "interview_notes": "Strong grasp of ORM, indexing, and authentication flows."
            }, token=self.employer_token, expected_status=200)

        # 5.10 Withdraw Application (JobSeeker)
        if self.created_app_id:
            self.request("DELETE", f"/applications/{self.created_app_id}/", token=self.jobseeker_token, expected_status=204)

        # 5.11 Cleanup JobSeeker Skill & Education/Experience
        if self.created_js_skill_id:
            self.request("DELETE", f"/jobseeker/skills/{self.created_js_skill_id}/", token=self.jobseeker_token, expected_status=204)
        if self.created_edu_id:
            self.request("DELETE", f"/jobseeker/education/{self.created_edu_id}/", token=self.jobseeker_token, expected_status=204)
        if self.created_exp_id:
            self.request("DELETE", f"/jobseeker/experience/{self.created_exp_id}/", token=self.jobseeker_token, expected_status=204)

        # 5.12 Logout JobSeeker
        if self.jobseeker_refresh:
            self.request("POST", "/auth/logout/", {
                "refresh": self.jobseeker_refresh
            }, token=self.jobseeker_token, expected_status=205)

        # -------------------------------------------------------------
        # FINAL REPORT & ERROR FILE GENERATION
        # -------------------------------------------------------------
        self.generate_report()

    def generate_report(self):
        end_time = datetime.now()
        total = self.tests_run
        passed = self.tests_passed
        failed = len(self.errors)
        
        print(f"\n{Colors.BOLD}{'='*80}")
        print(f" TEST RUN COMPLETE")
        print(f" Total Tests Run: {total}")
        print(f" Passed: {Colors.GREEN}{passed}{Colors.RESET}")
        print(f" Failed: {Colors.RED if failed > 0 else Colors.GREEN}{failed}{Colors.RESET}")
        print(f"{'='*80}{Colors.RESET}")

        if failed > 0:
            # Create the detailed error file requested by user!
            with open(self.error_file, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write(f"JOBCREST API ERROR REPORT\n")
                f.write(f"Generated at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Base URL: {self.base_url}\n")
                f.write(f"Total Tests: {total} | Passed: {passed} | FAILED: {failed}\n")
                f.write("=" * 80 + "\n\n")

                for idx, err in enumerate(self.errors, 1):
                    f.write(f"[{idx}] TEST FAILURE: {err['method']} {err['endpoint']}\n")
                    f.write(f"    Full URL:        {err['url']}\n")
                    f.write(f"    Timestamp:       {err['timestamp']}\n")
                    f.write(f"    Expected Status: {err['expected_status']}\n")
                    f.write(f"    Actual Status:   {err['actual_status']}\n")
                    f.write(f"    Failure Reason:  {err['error_reason']}\n")
                    if err['request_payload']:
                        f.write(f"    Request Body:\n")
                        f.write("      " + json.dumps(err['request_payload'], indent=2).replace("\n", "\n      ") + "\n")
                    f.write(f"    Response Body:\n")
                    if isinstance(err['response_body'], (dict, list)):
                        f.write("      " + json.dumps(err['response_body'], indent=2).replace("\n", "\n      ") + "\n")
                    else:
                        f.write(f"      {err['response_body']}\n")
                    f.write("-" * 80 + "\n\n")

            print(f"\n{Colors.RED}[!] Errors were encountered during API testing.{Colors.RESET}")
            print(f"{Colors.YELLOW}[i] Detailed error report has been written to: {os.path.abspath(self.error_file)}{Colors.RESET}\n")
        else:
            if os.path.exists(self.error_file):
                try:
                    os.remove(self.error_file)
                except Exception:
                    pass
            print(f"\n{Colors.GREEN}[OK] ALL {total} APIS PASSED WITH ZERO ERRORS! Clean run.{Colors.RESET}\n")


def main():
    parser = argparse.ArgumentParser(description="Run all JobCrest REST API tests")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"Base URL (default: {DEFAULT_BASE_URL})")
    parser.add_argument("--error-file", default=DEFAULT_ERROR_FILE, help=f"Error log output file (default: {DEFAULT_ERROR_FILE})")
    parser.add_argument("--no-auto-server", action="store_true", help="Do not attempt to auto-launch runserver if offline")
    args = parser.parse_args()

    runner = ApiTestRunner(base_url=args.base_url, error_file=args.error_file)
    runner.setup_seed_data()
    
    server_online = runner.check_server()
    server_proc = None
    
    if not server_online and not args.no_auto_server:
        print(f"{Colors.YELLOW}Starting Django development server automatically on 127.0.0.1:8000...{Colors.RESET}")
        try:
            server_proc = subprocess.Popen(
                [sys.executable, "manage.py", "runserver", "127.0.0.1:8000", "--noreload"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            for _ in range(20):
                time.sleep(0.5)
                if runner.check_server():
                    server_online = True
                    break
        except Exception as e:
            print(f"{Colors.RED}Failed to auto-start Django server: {e}{Colors.RESET}")
            
    if not server_online:
        print(f"{Colors.RED}ERROR: Django server is not reachable at {args.base_url}.{Colors.RESET}")
        print("Please start the server first using:")
        print("    python manage.py runserver")
        print("Then rerun this script:")
        print(f"    python run_api_tests.py\n")
        
        with open(args.error_file, "w", encoding="utf-8") as f:
            f.write(f"SERVER CONNECTION ERROR\nTimestamp: {datetime.now().isoformat()}\nCould not connect to {args.base_url}.\n")
        print(f"Connection failure logged to {args.error_file}")
        sys.exit(1)

    try:
        runner.run_all()
    finally:
        if server_proc:
            print(f"Stopping temporary background Django server...")
            server_proc.terminate()
            server_proc.wait()


if __name__ == "__main__":
    main()
