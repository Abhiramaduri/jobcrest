import uuid
from datetime import timedelta
from unittest.mock import patch
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import JobSeekerProfile
from companies.models import Company, EmployerProfile
from jobs.models import Job, JobCategory
from applications.models import Application, ApplicationStatusHistory, Interview

User = get_user_model()


class ApplicationAndInterviewUUIDSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Jobseeker
        self.seeker_user = User.objects.create_user(
            username="test_seeker_uuid",
            email="seeker_uuid@test.com",
            password="StrongPassword123!",
            user_type="jobseeker"
        )
        self.profile = JobSeekerProfile.objects.create(
            user=self.seeker_user,
            full_name="Seeker Testing UUIDs"
        )

        # Employer
        self.emp_user = User.objects.create_user(
            username="test_emp_uuid",
            email="recruiter_uuid@test.com",
            password="StrongPassword123!",
            user_type="employer"
        )
        self.company = Company.objects.create(name="Tech Corp", slug="tech-corp")
        self.emp_profile = EmployerProfile.objects.create(
            user=self.emp_user,
            company=self.company
        )
        self.job_cat = JobCategory.objects.create(name="Dev", slug="dev")
        self.job = Job.objects.create(
            title="Python Architect",
            company=self.company,
            posted_by=self.emp_profile,
            category=self.job_cat,
            description="Role info",
            responsibilities="Design system",
            job_type="full-time",
            status="published"
        )

    def test_apply_to_job_using_job_uuid(self):
        """Applying to job using the job's UUID returns an Application with UUID id."""
        self.client.force_authenticate(user=self.seeker_user)
        res = self.client.post("/api/applications/", {
            "job": str(self.job.uuid),
            "cover_letter": "I am interested in this role."
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        app_id = res.data.get("id")
        self.assertIsNotNone(app_id)
        # Verify app_id is a valid UUID
        parsed_uuid = uuid.UUID(str(app_id))
        self.assertIsInstance(parsed_uuid, uuid.UUID)

    def test_get_application_detail_via_uuid(self):
        """Application detail can be fetched via UUID."""
        app = Application.objects.create(job=self.job, applicant=self.profile)
        self.client.force_authenticate(user=self.seeker_user)
        res = self.client.get(f"/api/applications/{app.uuid}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("id"), str(app.uuid))

    def test_schedule_and_get_interview_via_uuid(self):
        """Schedule interview using Application UUID and fetch detail via Interview UUID."""
        app = Application.objects.create(job=self.job, applicant=self.profile)
        self.client.force_authenticate(user=self.emp_user)
        
        # Schedule interview passing application UUID
        res_schedule = self.client.post("/api/interviews/", {
            "application": str(app.uuid),
            "scheduled_at": "2026-12-01T10:00:00Z",
            "mode": "virtual",
            "meeting_link": "https://meet.google.com/abc-defg-hij"
        })
        self.assertEqual(res_schedule.status_code, status.HTTP_201_CREATED)
        interview_id = res_schedule.data.get("id")
        self.assertIsNotNone(interview_id)
        parsed_interview_uuid = uuid.UUID(str(interview_id))
        self.assertIsInstance(parsed_interview_uuid, uuid.UUID)

        # Retrieve interview via UUID
        res_get = self.client.get(f"/api/interviews/{interview_id}/")
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        self.assertEqual(res_get.data.get("id"), str(interview_id))


class ApplicationValidationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.seeker_user = User.objects.create_user(
            username="app_val_seeker",
            email="app_val_seeker@test.com",
            password="StrongPassword123!",
            user_type="jobseeker",
        )
        self.profile = JobSeekerProfile.objects.create(
            user=self.seeker_user,
            full_name="Validation Seeker",
        )
        self.emp_user = User.objects.create_user(
            username="app_val_emp",
            email="app_val_emp@test.com",
            password="StrongPassword123!",
            user_type="employer",
        )
        self.company = Company.objects.create(name="Val Corp", slug="val-corp", created_by=self.emp_user)
        self.emp_profile = EmployerProfile.objects.create(user=self.emp_user, company=self.company)
        self.job_cat = JobCategory.objects.create(name="Product", slug="product")

    def _create_job(self, slug, job_status="published", deadline=None):
        return Job.objects.create(
            title=f"Role {slug}",
            slug=slug,
            company=self.company,
            posted_by=self.emp_profile,
            category=self.job_cat,
            description="Job desc",
            responsibilities="Job resp",
            job_type="full-time",
            status=job_status,
            application_deadline=deadline,
        )

    def test_cannot_apply_to_unpublished_or_closed_job(self):
        """Draft, closed, and expired jobs reject applications with HTTP 400."""
        self.client.force_authenticate(user=self.seeker_user)
        for bad_status in ("draft", "closed", "expired"):
            job = self._create_job(f"job-{bad_status}", job_status=bad_status)
            res = self.client.post("/api/applications/", {"job": str(job.uuid), "cover_letter": "Hi"})
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("not accepting applications", str(res.data).lower())

    def test_cannot_apply_after_deadline_passed(self):
        """Published job whose application_deadline is in the past rejects applications with HTTP 400."""
        yesterday = timezone.localdate() - timedelta(days=1)
        expired_job = self._create_job("expired-deadline-job", job_status="published", deadline=yesterday)
        self.client.force_authenticate(user=self.seeker_user)
        res = self.client.post("/api/applications/", {"job": str(expired_job.uuid), "cover_letter": "Late"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("deadline", str(res.data).lower())

    def test_can_apply_on_deadline_day(self):
        """Published job whose application_deadline is today still accepts applications."""
        today = timezone.localdate()
        open_job = self._create_job("open-today-job", job_status="published", deadline=today)
        self.client.force_authenticate(user=self.seeker_user)
        res = self.client.post("/api/applications/", {"job": str(open_job.uuid), "cover_letter": "On time"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_duplicate_application_returns_clean_400(self):
        """Applying twice to the same published job returns HTTP 400 instead of DB IntegrityError 500."""
        job = self._create_job("dup-job", job_status="published")
        self.client.force_authenticate(user=self.seeker_user)
        res1 = self.client.post("/api/applications/", {"job": str(job.uuid), "cover_letter": "First"})
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        res2 = self.client.post("/api/applications/", {"job": str(job.uuid), "cover_letter": "Second"})
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already applied", str(res2.data).lower())

    def test_concurrent_duplicate_integrity_error_handled_gracefully(self):
        """Simulated race-condition IntegrityError returns clean HTTP 400."""
        job = self._create_job("race-job", job_status="published")
        self.client.force_authenticate(user=self.seeker_user)
        with patch("applications.serializers.ApplicationCreaterSerializer.save", side_effect=IntegrityError("unique constraint")):
            res = self.client.post("/api/applications/", {"job": str(job.uuid), "cover_letter": "Race"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already applied", res.data.get("detail", "").lower())


class ApplicationStateMachineAndWithdrawTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.seeker_user = User.objects.create_user(
            username="sm_seeker",
            email="sm_seeker@test.com",
            password="StrongPassword123!",
            user_type="jobseeker",
        )
        self.profile = JobSeekerProfile.objects.create(user=self.seeker_user, full_name="State Machine Seeker")

        self.emp_user = User.objects.create_user(
            username="sm_emp",
            email="sm_emp@test.com",
            password="StrongPassword123!",
            user_type="employer",
        )
        self.company = Company.objects.create(name="SM Corp", slug="sm-corp", created_by=self.emp_user)
        self.emp_profile = EmployerProfile.objects.create(user=self.emp_user, company=self.company)
        self.job_cat = JobCategory.objects.create(name="Data", slug="data")
        self.job = Job.objects.create(
            title="Data Scientist",
            slug="data-scientist",
            company=self.company,
            posted_by=self.emp_profile,
            category=self.job_cat,
            description="ML models",
            responsibilities="Build pipelines",
            job_type="full-time",
            status="published",
        )
        self.application = Application.objects.create(job=self.job, applicant=self.profile, status="applied")
        ApplicationStatusHistory.objects.create(
            application=self.application,
            old_status="",
            new_status="applied",
            changed_by=self.seeker_user,
            notes="Application submitted.",
        )

    def test_valid_forward_status_transitions_and_history_logging(self):
        """Allowed pipeline transitions succeed and append history entries."""
        self.client.force_authenticate(user=self.emp_user)
        for next_status in ("under_review", "shortlisted", "interview_scheduled", "hired"):
            res = self.client.patch(
                f"/api/applications/{self.application.uuid}/status/",
                {"status": next_status, "notes": f"Moved to {next_status}"},
            )
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(res.data["status"], next_status)

        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "hired")
        self.assertEqual(self.application.history.count(), 5)

    def test_invalid_status_transitions_blocked_with_400(self):
        """Backward and terminal transitions (e.g., rejected -> applied, under_review -> applied) are rejected."""
        self.client.force_authenticate(user=self.emp_user)

        # Move to under_review -> cannot revert to applied
        res_review = self.client.patch(f"/api/applications/{self.application.uuid}/status/", {"status": "under_review"})
        self.assertEqual(res_review.status_code, status.HTTP_200_OK)

        res_backward = self.client.patch(f"/api/applications/{self.application.uuid}/status/", {"status": "applied"})
        self.assertEqual(res_backward.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("invalid status transition", str(res_backward.data).lower())

        # Employer cannot set status to withdrawn directly
        res_emp_withdraw = self.client.patch(f"/api/applications/{self.application.uuid}/status/", {"status": "withdrawn"})
        self.assertEqual(res_emp_withdraw.status_code, status.HTTP_400_BAD_REQUEST)

        # Reject application -> terminal state cannot transition back to applied or hired
        res_reject = self.client.patch(f"/api/applications/{self.application.uuid}/status/", {"status": "rejected"})
        self.assertEqual(res_reject.status_code, status.HTTP_200_OK)

        for target in ("applied", "under_review", "shortlisted", "interview_scheduled", "hired"):
            res_invalid = self.client.patch(f"/api/applications/{self.application.uuid}/status/", {"status": target})
            self.assertEqual(res_invalid.status_code, status.HTTP_400_BAD_REQUEST)

        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "rejected")

    def test_status_update_and_history_insert_are_atomic(self):
        """If history insertion fails inside transaction.atomic(), status update rolls back."""
        self.client.force_authenticate(user=self.emp_user)
        with patch(
            "applications.views.ApplicationStatusHistory.objects.create",
            side_effect=RuntimeError("Simulated DB error during history insert"),
        ):
            with self.assertRaises(RuntimeError):
                self.client.patch(
                    f"/api/applications/{self.application.uuid}/status/",
                    {"status": "under_review", "notes": "Should rollback"},
                )

        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "applied")

    def test_withdraw_sets_withdrawn_status_and_preserves_history(self):
        """Withdrawing marks status='withdrawn' instead of hard deleting, preserving history for employer."""
        # Employer moves to under_review first
        self.client.force_authenticate(user=self.emp_user)
        self.client.patch(
            f"/api/applications/{self.application.uuid}/status/",
            {"status": "under_review", "notes": "Screening started"},
        )

        # Applicant withdraws
        self.client.force_authenticate(user=self.seeker_user)
        res_withdraw = self.client.delete(f"/api/applications/{self.application.uuid}/")
        self.assertEqual(res_withdraw.status_code, status.HTTP_200_OK)
        self.assertEqual(res_withdraw.data["status"], "withdrawn")

        # Application row still exists in DB with preserved history
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, "withdrawn")
        self.assertEqual(self.application.history.count(), 3)

        # Withdrawing a second time is rejected with 400
        res_withdraw_again = self.client.delete(f"/api/applications/{self.application.uuid}/")
        self.assertEqual(res_withdraw_again.status_code, status.HTTP_400_BAD_REQUEST)

        # Employer can still inspect the withdrawn application & full history via UUID
        self.client.force_authenticate(user=self.emp_user)
        res_emp_detail = self.client.get(f"/api/applications/{self.application.uuid}/")
        self.assertEqual(res_emp_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(res_emp_detail.data["status"], "withdrawn")

        res_emp_history = self.client.get(f"/api/applications/{self.application.uuid}/history/")
        self.assertEqual(res_emp_history.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_emp_history.data), 3)
        self.assertEqual(res_emp_history.data[0]["new_status"], "withdrawn")

        # Employer cannot transition or schedule interview on withdrawn application
        res_emp_update = self.client.patch(f"/api/applications/{self.application.uuid}/status/", {"status": "hired"})
        self.assertEqual(res_emp_update.status_code, status.HTTP_400_BAD_REQUEST)

        res_interview = self.client.post("/api/interviews/", {
            "application": str(self.application.uuid),
            "scheduled_at": "2026-12-05T10:00:00Z",
            "mode": "virtual",
        })
        self.assertEqual(res_interview.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Interview.objects.filter(application=self.application).count(), 0)
