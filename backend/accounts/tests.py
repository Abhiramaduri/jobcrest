import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import JobSeekerProfile
from accounts.resume_security import (
    generate_signed_resume_url,
    verify_signed_resume_token,
    RESUME_SIGNER_SALT
)
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from companies.models import Company, EmployerProfile
from jobs.models import Job, JobCategory
from applications.models import Application

User = get_user_model()


class CandidatePrivacyAndResumeSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Candidate 1 (Owner)
        self.candidate_user = User.objects.create_user(
            username="candidate1",
            email="candidate1@example.com",
            password="StrongPassword123!",
            user_type="jobseeker"
        )
        self.profile = JobSeekerProfile.objects.create(
            user=self.candidate_user,
            full_name="Alex Candidate",
            headline="Full Stack Engineer",
            current_ctc=1200000.00,
            expected_ctc=1800000.00,
            resume=SimpleUploadedFile("alex_resume.pdf", b"%PDF-1.4 test resume content", content_type="application/pdf")
        )

        # Candidate 2 (Attacker / Competing Candidate)
        self.other_candidate = User.objects.create_user(
            username="candidate2",
            email="candidate2@example.com",
            password="StrongPassword123!",
            user_type="jobseeker"
        )
        self.other_profile = JobSeekerProfile.objects.create(
            user=self.other_candidate,
            full_name="Bob Other",
            headline="Junior Developer"
        )

        # Employer 1 (Without application)
        self.unauth_emp_user = User.objects.create_user(
            username="employer_unauth",
            email="recruiter_unauth@compb.com",
            password="StrongPassword123!",
            user_type="employer"
        )
        self.company_b = Company.objects.create(name="Company B", slug="company-b")
        self.emp_profile_b = EmployerProfile.objects.create(
            user=self.unauth_emp_user,
            company=self.company_b
        )

        # Employer 2 (With active application from candidate 1)
        self.auth_emp_user = User.objects.create_user(
            username="employer_auth",
            email="recruiter_auth@compa.com",
            password="StrongPassword123!",
            user_type="employer"
        )
        self.company_a = Company.objects.create(name="Company A", slug="company-a")
        self.emp_profile_a = EmployerProfile.objects.create(
            user=self.auth_emp_user,
            company=self.company_a
        )
        self.job_cat = JobCategory.objects.create(name="Engineering", slug="engineering")
        self.job = Job.objects.create(
            title="Senior Backend Engineer",
            company=self.company_a,
            posted_by=self.emp_profile_a,
            category=self.job_cat,
            description="Looking for Python pro",
            responsibilities="Design APIs",
            job_type="full-time"
        )
        self.application = Application.objects.create(
            job=self.job,
            applicant=self.profile,
            status="applied"
        )

    def test_jobseeker_profile_has_uuid(self):
        self.assertIsNotNone(self.profile.uuid)
        self.assertIsInstance(self.profile.uuid, uuid.UUID)

    def test_owner_can_access_own_profile_via_uuid(self):
        self.client.force_authenticate(user=self.candidate_user)
        res = self.client.get(f"/api/jobseeker/profile/{self.profile.uuid}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("full_name"), "Alex Candidate")
        self.assertEqual(res.data.get("uuid"), str(self.profile.uuid))
        # Ensure resume is converted to signed URL
        self.assertIn("/api/jobseeker/resume/download/?token=", res.data.get("resume"))

    def test_competing_jobseeker_denied_access(self):
        """Another jobseeker must receive 403 Forbidden when trying to view candidate's profile."""
        self.client.force_authenticate(user=self.other_candidate)
        res = self.client.get(f"/api/jobseeker/profile/{self.profile.uuid}/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You do not have permission", res.data.get("detail", ""))

    def test_employer_without_application_denied_access(self):
        """An employer who has no application from this candidate must be denied with 403 Forbidden."""
        self.client.force_authenticate(user=self.unauth_emp_user)
        res = self.client.get(f"/api/jobseeker/profile/{self.profile.uuid}/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("You do not have permission", res.data.get("detail", ""))

    def test_employer_with_application_granted_access(self):
        """An employer who received an application from this candidate is allowed access."""
        self.client.force_authenticate(user=self.auth_emp_user)
        res = self.client.get(f"/api/jobseeker/profile/{self.profile.uuid}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("full_name"), "Alex Candidate")
        self.assertIn("/api/jobseeker/resume/download/?token=", res.data.get("resume"))

    def test_unauthenticated_user_denied(self):
        """Anonymous user must receive 401 Unauthorized."""
        res = self.client.get(f"/api/jobseeker/profile/{self.profile.uuid}/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_signed_resume_url_download_success(self):
        """Downloading via valid signed token succeeds."""
        signed_url = generate_signed_resume_url(self.profile.resume.name)
        res = self.client.get(signed_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.headers.get("Content-Type"), "application/pdf")

    def test_tampered_resume_token_denied(self):
        """Tampered token is rejected with 403 Forbidden."""
        signed_url = generate_signed_resume_url(self.profile.resume.name)
        tampered_url = signed_url + "evil"
        res = self.client.get(tampered_url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Invalid or tampered", res.data.get("detail", ""))

    def test_expired_resume_token_denied(self):
        """Expired token is rejected with 403 Forbidden."""
        signer = TimestampSigner(salt=RESUME_SIGNER_SALT)
        expired_token = signer.sign(self.profile.resume.name)
        with self.assertRaises(SignatureExpired):
            verify_signed_resume_token(expired_token, max_age=-1)

    def test_direct_media_resume_access_forbidden(self):
        """Direct access to media/resume/ is blocked with 403 Forbidden."""
        res = self.client.get(f"/media/resume/{self.profile.resume.name}")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class ResumeUploadValidationAndStorageTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Jobseeker user
        self.user = User.objects.create_user(
            username="resumetester",
            email="tester@example.com",
            password="StrongPassword123!",
            user_type="jobseeker"
        )
        self.profile = JobSeekerProfile.objects.create(
            user=self.user,
            full_name="Tester Candidate"
        )
        self.upload_url = "/api/jobseeker/profile/resume/"

    def test_upload_valid_pdf_success(self):
        """Valid PDF with legitimate %PDF- signature uploads successfully."""
        self.client.force_authenticate(user=self.user)
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
        upload = SimpleUploadedFile("my_resume.pdf", pdf_content, content_type="application/pdf")

        res = self.client.post(self.upload_url, {"resume": upload}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertTrue(bool(self.profile.resume))
        self.assertTrue(self.profile.resume.name.endswith(".pdf"))
        self.assertIn("/api/jobseeker/resume/download/?token=", res.data.get("resume"))

    def test_upload_valid_doc_success(self):
        """Valid DOC file with legitimate OLE header uploads successfully."""
        self.client.force_authenticate(user=self.user)
        doc_header = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 64
        upload = SimpleUploadedFile("legacy_resume.doc", doc_header, content_type="application/msword")

        res = self.client.post(self.upload_url, {"resume": upload}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertTrue(bool(self.profile.resume))
        self.assertTrue(self.profile.resume.name.endswith(".doc"))

    def test_upload_valid_docx_success(self):
        """Valid DOCX file with legitimate ZIP header uploads successfully."""
        self.client.force_authenticate(user=self.user)
        docx_header = b"PK\x03\x04" + b"\x14\x00\x06\x00" + b"\x00" * 32
        upload = SimpleUploadedFile(
            "modern_resume.docx",
            docx_header,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        res = self.client.post(self.upload_url, {"resume": upload}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertTrue(bool(self.profile.resume))
        self.assertTrue(self.profile.resume.name.endswith(".docx"))

    def test_upload_disallowed_extension_rejected(self):
        """Uploading dangerous executable or script formats (.exe, .sh, .py, .txt) is rejected."""
        self.client.force_authenticate(user=self.user)

        disallowed_files = [
            ("malicious.exe", b"MZ\x90\x00\x03\x00\x00\x00", "application/x-msdownload"),
            ("script.sh", b"#!/bin/bash\necho test", "application/x-sh"),
            ("backdoor.py", b"import os\nos.system('whoami')", "text/x-python"),
            ("notes.txt", b"Just plain text", "text/plain"),
        ]

        for filename, content, mime in disallowed_files:
            upload = SimpleUploadedFile(filename, content, content_type=mime)
            res = self.client.post(self.upload_url, {"resume": upload}, format="multipart")
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            detail = res.data.get("detail", "")
            self.assertTrue(
                "Unsupported file" in detail or "not allowed" in detail or "Only PDF" in detail,
                f"Expected extension rejection message for {filename}, got: {detail}"
            )

    def test_upload_exceeds_size_limit_rejected(self):
        """File larger than 5 MB is rejected."""
        self.client.force_authenticate(user=self.user)
        # Create a file slightly larger than 5 MB (5.1 MB)
        oversized_content = b"%PDF-1.4 " + (b"A" * (5 * 1024 * 1024 + 1024))
        upload = SimpleUploadedFile("huge_resume.pdf", oversized_content, content_type="application/pdf")

        res = self.client.post(self.upload_url, {"resume": upload}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("limit", res.data.get("detail", "").lower())

    def test_upload_empty_file_rejected(self):
        """Zero-byte file is rejected."""
        self.client.force_authenticate(user=self.user)
        upload = SimpleUploadedFile("empty.pdf", b"", content_type="application/pdf")

        res = self.client.post(self.upload_url, {"resume": upload}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("empty", res.data.get("detail", "").lower())

    def test_upload_spoofed_extension_magic_bytes_mismatch_rejected(self):
        """File named .pdf but containing non-PDF binary signature is rejected."""
        self.client.force_authenticate(user=self.user)
        spoofed_content = b"<?php echo 'malicious webshell'; ?>"
        upload = SimpleUploadedFile("fake.pdf", spoofed_content, content_type="application/pdf")

        res = self.client.post(self.upload_url, {"resume": upload}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("corrupt or disguised", res.data.get("detail", "").lower())

    def test_upload_disallowed_mime_type_rejected(self):
        """PDF file with executable MIME type is rejected."""
        self.client.force_authenticate(user=self.user)
        upload = SimpleUploadedFile("test.pdf", b"%PDF-1.4 legitimate header", content_type="application/x-msdownload")

        res = self.client.post(self.upload_url, {"resume": upload}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid MIME type", res.data.get("detail", ""))

    def test_upload_without_file_rejected(self):
        """POST without 'resume' file payload returns 400 Bad Request."""
        self.client.force_authenticate(user=self.user)
        res = self.client.post(self.upload_url, {}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No resume file provided", res.data.get("detail", ""))

    def test_upload_unauthenticated_rejected(self):
        """Anonymous user cannot upload resume."""
        upload = SimpleUploadedFile("test.pdf", b"%PDF-1.4 test", content_type="application/pdf")
        res = self.client.post(self.upload_url, {"resume": upload}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_as_employer_forbidden(self):
        """Employer user cannot upload resume (only JobSeekers)."""
        emp_user = User.objects.create_user(
            username="emp1",
            email="emp1@example.com",
            password="StrongPassword123!",
            user_type="employer"
        )
        self.client.force_authenticate(user=emp_user)
        upload = SimpleUploadedFile("test.pdf", b"%PDF-1.4 test", content_type="application/pdf")
        res = self.client.post(self.upload_url, {"resume": upload}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_resume_replacement_deletes_old_file(self):
        """Uploading a new resume removes the previously uploaded file from storage."""
        self.client.force_authenticate(user=self.user)
        pdf_1 = SimpleUploadedFile("first.pdf", b"%PDF-1.4 first resume", content_type="application/pdf")
        res1 = self.client.post(self.upload_url, {"resume": pdf_1}, format="multipart")
        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        first_storage_name = self.profile.resume.name
        from django.core.files.storage import default_storage
        self.assertTrue(default_storage.exists(first_storage_name))

        # Upload replacement resume
        pdf_2 = SimpleUploadedFile("second.pdf", b"%PDF-1.4 second resume", content_type="application/pdf")
        res2 = self.client.post(self.upload_url, {"resume": pdf_2}, format="multipart")
        self.assertEqual(res2.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.assertNotEqual(self.profile.resume.name, first_storage_name)
        # Previous file should have been deleted from storage
        self.assertFalse(default_storage.exists(first_storage_name))
        self.assertTrue(default_storage.exists(self.profile.resume.name))

    def test_resume_download_uses_storage_backend(self):
        """Resume download retrieves files via default_storage abstraction."""
        self.client.force_authenticate(user=self.user)
        pdf = SimpleUploadedFile("download_test.pdf", b"%PDF-1.4 downloadable resume content", content_type="application/pdf")
        res_upload = self.client.post(self.upload_url, {"resume": pdf}, format="multipart")
        self.assertEqual(res_upload.status_code, status.HTTP_200_OK)

        signed_url = res_upload.data.get("resume")
        res_download = self.client.get(signed_url)
        self.assertEqual(res_download.status_code, status.HTTP_200_OK)
        self.assertEqual(res_download.headers.get("Content-Type"), "application/pdf")
        self.assertIn("inline", res_download.headers.get("Content-Disposition"))

    def test_cloud_storage_django_storages_backend_availability(self):
        """Verify that django-storages S3Storage is importable and configurable."""
        from storages.backends.s3 import S3Storage
        self.assertIsNotNone(S3Storage)


class AuthRateLimitingAndLockoutTests(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.client = APIClient()
        self.test_user = User.objects.create_user(
            username="ratelimituser",
            email="ratelimit@example.com",
            password="StrongPassword123!",
            user_type="jobseeker"
        )

    def tearDown(self):
        from django.core.cache import cache
        cache.clear()

    def test_login_rate_limiting_enforced(self):
        """Excessive rapid login requests trigger HTTP 429 Too Many Requests."""
        for i in range(5):
            res = self.client.post(
                "/api/auth/login/",
                {"username": "ratelimituser", "password": "wrongpassword"},
                HTTP_X_FORWARDED_FOR="203.0.113.10"
            )
            self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_429_TOO_MANY_REQUESTS])

        # 6th attempt triggers 429 Too Many Requests
        res = self.client.post(
            "/api/auth/login/",
            {"username": "ratelimituser", "password": "wrongpassword"},
            HTTP_X_FORWARDED_FOR="203.0.113.10"
        )
        self.assertEqual(res.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_consecutive_failed_logins_trigger_account_lockout(self):
        """5 consecutive failed logins trigger lockout protection even across distributed IPs."""
        # First 4 failed attempts return 401 with remaining attempts warning
        for i in range(4):
            res = self.client.post(
                "/api/auth/login/",
                {"username": "ratelimituser", "password": "badpassword1"},
                HTTP_X_FORWARDED_FOR=f"198.51.100.{i + 1}"
            )
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertIn("remaining before temporary lockout", res.data.get("detail", ""))

        # 5th failed attempt hits threshold (5) and immediately triggers lockout (HTTP 429)
        res_5th = self.client.post(
            "/api/auth/login/",
            {"username": "ratelimituser", "password": "badpassword1"},
            HTTP_X_FORWARDED_FOR="198.51.100.5"
        )
        self.assertEqual(res_5th.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn("locked", res_5th.data.get("detail", "").lower())

        # 6th attempt from a fresh IP (IP throttle not hit) remains blocked by account lockout
        res_locked = self.client.post(
            "/api/auth/login/",
            {"username": "ratelimituser", "password": "StrongPassword123!"},
            HTTP_X_FORWARDED_FOR="198.51.100.99"
        )
        self.assertEqual(res_locked.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn("locked", res_locked.data.get("detail", "").lower())

        from accounts.throttles import is_account_locked
        locked, remaining = is_account_locked("ratelimituser", "198.51.100.99")
        self.assertTrue(locked)
        self.assertGreater(remaining, 0)

    def test_successful_login_clears_failure_counter(self):
        """Successful authentication resets any previously accumulated failed attempts."""
        # 2 failed attempts
        for _ in range(2):
            self.client.post(
                "/api/auth/login/",
                {"username": "ratelimituser", "password": "bad"},
                HTTP_X_FORWARDED_FOR="198.51.100.50"
            )

        # Successful login
        res_success = self.client.post(
            "/api/auth/login/",
            {"username": "ratelimituser", "password": "StrongPassword123!"},
            HTTP_X_FORWARDED_FOR="198.51.100.50"
        )
        self.assertEqual(res_success.status_code, status.HTTP_200_OK)

        from accounts.throttles import is_account_locked
        locked, _ = is_account_locked("ratelimituser", "198.51.100.50")
        self.assertFalse(locked)

    def test_send_registration_otp_rate_limiting(self):
        """Spamming send-otp endpoint triggers 429 Too Many Requests."""
        for i in range(5):
            res = self.client.post(
                "/api/auth/register/send-otp/",
                {"email": f"unique{i}@example.com"},
                HTTP_X_FORWARDED_FOR="203.0.113.88"
            )
            self.assertIn(res.status_code, [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_429_TOO_MANY_REQUESTS])

        res_exceeded = self.client.post(
            "/api/auth/register/send-otp/",
            {"email": "another@example.com"},
            HTTP_X_FORWARDED_FOR="203.0.113.88"
        )
        self.assertEqual(res_exceeded.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_password_reset_request_rate_limiting(self):
        """Spamming password reset triggers 429 Too Many Requests."""
        for _ in range(3):
            self.client.post(
                "/api/auth/password-reset/",
                {"email": "ratelimit@example.com"},
                HTTP_X_FORWARDED_FOR="203.0.113.99"
            )

        res_blocked = self.client.post(
            "/api/auth/password-reset/",
            {"email": "ratelimit@example.com"},
            HTTP_X_FORWARDED_FOR="203.0.113.99"
        )
        self.assertEqual(res_blocked.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_health_check_endpoint(self):
        """Health check returns 200 OK and is unthrottled for load balancers."""
        res = self.client.get("/api/health/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("status"), "healthy")
        self.assertEqual(res.data.get("database"), "connected")

        # Root healthz path for load balancers
        res_root = self.client.get("/healthz")
        self.assertEqual(res_root.status_code, status.HTTP_200_OK)
        self.assertEqual(res_root.data.get("status"), "healthy")


class LogoutTokenErrorTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="logout_user",
            email="logout_user@example.com",
            password="StrongPassword123!",
            user_type="jobseeker",
        )

    def test_logout_with_valid_token_succeeds_and_blacklists(self):
        """Valid refresh token returns 205 Reset Content and cannot be reused."""
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = str(RefreshToken.for_user(self.user))

        self.client.force_authenticate(user=self.user)
        res = self.client.post("/api/auth/logout/", {"refresh": refresh})
        self.assertEqual(res.status_code, status.HTTP_205_RESET_CONTENT)

        # Re-submitting blacklisted token returns 400 (not 500)
        res_reuse = self.client.post("/api/auth/logout/", {"refresh": refresh})
        self.assertEqual(res_reuse.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_with_invalid_or_missing_token_returns_400_not_500(self):
        """Missing or malformed refresh token returns HTTP 400 instead of 500."""
        self.client.force_authenticate(user=self.user)

        res_missing = self.client.post("/api/auth/logout/", {})
        self.assertEqual(res_missing.status_code, status.HTTP_400_BAD_REQUEST)

        res_bad = self.client.post("/api/auth/logout/", {"refresh": "not-a-valid-jwt-token"})
        self.assertEqual(res_bad.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("invalid or expired", res_bad.data.get("detail", "").lower())

