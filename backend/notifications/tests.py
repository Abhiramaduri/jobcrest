import uuid
from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import JobSeekerProfile, OTPVerification
from companies.models import Company, EmployerProfile
from jobs.models import Job, JobCategory
from notifications.emails import generate_email_verification_token
from notifications.models import Notification

User = get_user_model()


class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="notif_user",
            email="notif_user@example.com",
            password="StrongPassword123!",
            user_type="jobseeker",
        )

    def test_notification_creation_defaults_and_uuid(self):
        """Notification assigns unique UUID, defaults to unread general type, and formats __str__."""
        notif = Notification.objects.create(
            user=self.user,
            title="Welcome to JobCrest",
            message="Complete your profile to start applying.",
        )
        self.assertIsNotNone(notif.uuid)
        self.assertIsInstance(notif.uuid, uuid.UUID)
        self.assertEqual(notif.notification_type, "general")
        self.assertFalse(notif.is_read)
        self.assertEqual(str(notif), "Welcome to JobCrest")

    def test_notification_types_and_mark_read(self):
        """Notifications support all defined types and updating read state."""
        notif = Notification.objects.create(
            user=self.user,
            title="Interview Scheduled",
            message="Your interview is confirmed for tomorrow.",
            notification_type="interview_scheduled",
        )
        self.assertEqual(notif.notification_type, "interview_scheduled")

        notif.is_read = True
        notif.save(update_fields=["is_read"])
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_notification_cascade_deleted_with_user(self):
        """Deleting the user removes associated notifications via CASCADE."""
        Notification.objects.create(
            user=self.user,
            title="Application Update",
            message="Your application is under review.",
            notification_type="application_update",
        )
        self.assertEqual(Notification.objects.count(), 1)
        self.user.delete()
        self.assertEqual(Notification.objects.count(), 0)


class NotificationSignalAndAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.seeker_user = User.objects.create_user(
            username="notif_seeker",
            email="notif_seeker@example.com",
            password="StrongPassword123!",
            user_type="jobseeker",
        )
        self.seeker_profile = JobSeekerProfile.objects.create(
            user=self.seeker_user,
            full_name="Notif Seeker",
        )

        self.emp_user = User.objects.create_user(
            username="notif_emp",
            email="notif_emp@example.com",
            password="StrongPassword123!",
            user_type="employer",
        )
        self.company = Company.objects.create(name="Notif Corp", slug="notif-corp", created_by=self.emp_user)
        self.emp_profile = EmployerProfile.objects.create(user=self.emp_user, company=self.company)
        self.category = JobCategory.objects.create(name="Platform", slug="platform")
        self.job = Job.objects.create(
            title="Staff Engineer",
            slug="staff-engineer",
            company=self.company,
            posted_by=self.emp_profile,
            category=self.category,
            description="Platform engineering",
            responsibilities="Build scalable systems",
            job_type="full-time",
            status="published",
        )

    def test_notifications_created_across_application_and_interview_lifecycle(self):
        """Applying, updating status, scheduling interview, and withdrawing automatically create notifications."""
        # 1. Jobseeker applies -> Employer receives notification
        self.client.force_authenticate(user=self.seeker_user)
        res_apply = self.client.post("/api/applications/", {"job": str(self.job.uuid), "cover_letter": "Hello"})
        self.assertEqual(res_apply.status_code, status.HTTP_201_CREATED)
        app_uuid = res_apply.data["id"]

        emp_notifs = Notification.objects.filter(user=self.emp_user)
        self.assertEqual(emp_notifs.count(), 1)
        self.assertEqual(emp_notifs.first().notification_type, "application_update")
        self.assertIn("New Application", emp_notifs.first().title)

        # 2. Employer updates status -> Applicant receives application_update notification
        self.client.force_authenticate(user=self.emp_user)
        res_status = self.client.patch(
            f"/api/applications/{app_uuid}/status/",
            {"status": "under_review", "notes": "Reviewing"},
        )
        self.assertEqual(res_status.status_code, status.HTTP_200_OK)

        seeker_notifs = Notification.objects.filter(user=self.seeker_user).order_by("created_at")
        self.assertEqual(seeker_notifs.count(), 1)
        self.assertEqual(seeker_notifs.first().notification_type, "application_update")
        self.assertIn("Under Review", seeker_notifs.first().message)

        # 3. Employer schedules interview -> Applicant receives interview_scheduled notification
        res_interview = self.client.post("/api/interviews/", {
            "application": app_uuid,
            "scheduled_at": "2026-12-10T10:00:00Z",
            "mode": "virtual",
            "meeting_link": "https://meet.example.com/staff",
        })
        self.assertEqual(res_interview.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.filter(user=self.seeker_user).count(), 2)
        latest_seeker_notif = Notification.objects.filter(user=self.seeker_user).order_by("-created_at").first()
        self.assertEqual(latest_seeker_notif.notification_type, "interview_scheduled")

        # 4. Jobseeker withdraws -> Employer receives withdrawal notification
        self.client.force_authenticate(user=self.seeker_user)
        res_withdraw = self.client.delete(f"/api/applications/{app_uuid}/")
        self.assertEqual(res_withdraw.status_code, status.HTTP_200_OK)
        self.assertEqual(Notification.objects.filter(user=self.emp_user).count(), 2)
        latest_emp_notif = Notification.objects.filter(user=self.emp_user).order_by("-created_at").first()
        self.assertIn("Withdrawn", latest_emp_notif.title)

    def test_notification_endpoints_list_unread_count_and_mark_read(self):
        """GET /notifications/, unread-count, mark-read, and mark-all-read work accurately."""
        n1 = Notification.objects.create(user=self.seeker_user, title="N1", message="First", notification_type="application_update")
        n2 = Notification.objects.create(user=self.seeker_user, title="N2", message="Second", notification_type="interview_scheduled")

        self.client.force_authenticate(user=self.seeker_user)

        # List all
        res_list = self.client.get("/api/notifications/")
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(res_list.data["count"], 2)
        self.assertEqual(len(res_list.data["results"]), 2)

        # Unread count == 2
        res_count = self.client.get("/api/notifications/unread-count/")
        self.assertEqual(res_count.status_code, status.HTTP_200_OK)
        self.assertEqual(res_count.data["unread_count"], 2)

        # Mark n1 as read via UUID
        res_read = self.client.patch(f"/api/notifications/{n1.uuid}/read/")
        self.assertEqual(res_read.status_code, status.HTTP_200_OK)
        self.assertTrue(res_read.data["is_read"])

        # Unread count == 1 and ?is_read=false returns only n2
        res_count_after = self.client.get("/api/notifications/unread-count/")
        self.assertEqual(res_count_after.data["unread_count"], 1)

        res_unread_only = self.client.get("/api/notifications/?is_read=false")
        self.assertEqual(res_unread_only.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_unread_only.data["results"]), 1)
        self.assertEqual(res_unread_only.data["results"][0]["id"], str(n2.uuid))

        # Mark all read
        res_all = self.client.post("/api/notifications/mark-all-read/")
        self.assertEqual(res_all.status_code, status.HTTP_200_OK)
        self.assertEqual(res_all.data["updated"], 1)
        self.assertEqual(res_all.data["unread_count"], 0)
        self.assertEqual(Notification.objects.filter(user=self.seeker_user, is_read=False).count(), 0)

    def test_notifications_require_auth_and_enforce_ownership(self):
        """Unauthenticated callers get 401 and users cannot mark another user's notifications read."""
        emp_notif = Notification.objects.create(user=self.emp_user, title="Private", message="Employer only")

        # Anonymous -> 401
        self.assertEqual(self.client.get("/api/notifications/").status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.get("/api/notifications/unread-count/").status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.patch(f"/api/notifications/{emp_notif.uuid}/read/").status_code, status.HTTP_401_UNAUTHORIZED)

        # Jobseeker trying to read/mark Employer's notification -> 404 (isolated queryset)
        self.client.force_authenticate(user=self.seeker_user)
        res_other = self.client.patch(f"/api/notifications/{emp_notif.uuid}/read/")
        self.assertEqual(res_other.status_code, status.HTTP_404_NOT_FOUND)
        emp_notif.refresh_from_db()
        self.assertFalse(emp_notif.is_read)


class TransactionalEmailTests(TestCase):
    def setUp(self):
        cache.clear()
        mail.outbox.clear()
        self.client = APIClient()

        self.seeker_user = User.objects.create_user(
            username="email_seeker",
            email="email_seeker@example.com",
            password="StrongPassword123!",
            user_type="jobseeker",
        )
        self.seeker_profile = JobSeekerProfile.objects.create(
            user=self.seeker_user,
            full_name="Email Seeker",
        )

        self.emp_user = User.objects.create_user(
            username="email_emp",
            email="email_emp@example.com",
            password="StrongPassword123!",
            user_type="employer",
        )
        self.company = Company.objects.create(name="MailCorp", slug="mailcorp", created_by=self.emp_user)
        self.emp_profile = EmployerProfile.objects.create(user=self.emp_user, company=self.company)
        self.category = JobCategory.objects.create(name="Backend", slug="backend")
        self.job = Job.objects.create(
            title="Distributed Systems Engineer",
            slug="distributed-systems-engineer",
            company=self.company,
            posted_by=self.emp_profile,
            category=self.category,
            description="Distributed systems",
            responsibilities="Design consensus services",
            job_type="full-time",
            status="published",
        )

    def tearDown(self):
        cache.clear()

    def test_registration_sends_otp_and_welcome_emails(self):
        """OTP verification email and Welcome email are both sent with HTML alternatives."""
        res_otp = self.client.post(
            "/api/auth/register/send-otp/",
            {"email": "newjoiner@example.com"},
            HTTP_X_FORWARDED_FOR="203.0.113.111",
        )
        self.assertEqual(res_otp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        otp_email = mail.outbox[0]
        self.assertEqual(otp_email.to, ["newjoiner@example.com"])
        self.assertIn("Verification Code", otp_email.subject)
        self.assertTrue(any(alt[1] == "text/html" for alt in otp_email.alternatives))

        otp_code = OTPVerification.objects.filter(email="newjoiner@example.com", purpose="registration").first().otp
        mail.outbox.clear()

        res_reg = self.client.post(
            "/api/auth/register/",
            {
                "username": "newjoiner",
                "email": "newjoiner@example.com",
                "otp": otp_code,
                "password": "StrongPassword123!",
                "password2": "StrongPassword123!",
                "user_type": "jobseeker",
            },
            HTTP_X_FORWARDED_FOR="203.0.113.111",
        )
        self.assertEqual(res_reg.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        welcome_email = mail.outbox[0]
        self.assertEqual(welcome_email.to, ["newjoiner@example.com"])
        self.assertIn("Welcome to JobCrest", welcome_email.subject)
        self.assertTrue(any(alt[1] == "text/html" for alt in welcome_email.alternatives))

    def test_verify_email_signed_link_flow(self):
        """Signed verify-email flow marks unverified user verified and sends welcome email."""
        unverified = User.objects.create_user(
            username="unverified_user",
            email="unverified@example.com",
            password="StrongPassword123!",
            user_type="employer",
            is_verified=False,
        )
        self.client.force_authenticate(user=unverified)
        res_send = self.client.post("/api/auth/verify-email/send/", HTTP_X_FORWARDED_FOR="203.0.113.112")
        self.assertEqual(res_send.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Verify Your JobCrest Email", mail.outbox[0].subject)

        token = generate_email_verification_token(unverified)
        mail.outbox.clear()

        # Tampered token rejected
        res_bad = self.client.get("/api/auth/verify-email/?token=tampered-token", HTTP_X_FORWARDED_FOR="203.0.113.112")
        self.assertEqual(res_bad.status_code, status.HTTP_400_BAD_REQUEST)

        # Valid token verifies user and sends welcome email
        res_ok = self.client.get(f"/api/auth/verify-email/?token={token}", HTTP_X_FORWARDED_FOR="203.0.113.112")
        self.assertEqual(res_ok.status_code, status.HTTP_200_OK)
        unverified.refresh_from_db()
        self.assertTrue(unverified.is_verified)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Welcome to JobCrest", mail.outbox[0].subject)

        # Re-sending verification when already verified returns 400
        res_already = self.client.post("/api/auth/verify-email/send/", HTTP_X_FORWARDED_FOR="203.0.113.112")
        self.assertEqual(res_already.status_code, status.HTTP_400_BAD_REQUEST)

    def test_application_received_status_update_and_interview_ics_emails(self):
        """Applying, updating status, scheduling/rescheduling interview (with .ics), and withdrawing dispatch emails."""
        # 1. Apply -> Application Received (to applicant) + New Application (to employer)
        self.client.force_authenticate(user=self.seeker_user)
        res_apply = self.client.post("/api/applications/", {"job": str(self.job.uuid), "cover_letter": "Excited!"})
        self.assertEqual(res_apply.status_code, status.HTTP_201_CREATED)
        app_uuid = res_apply.data["id"]

        self.assertEqual(len(mail.outbox), 2)
        recipients = {m.to[0]: m for m in mail.outbox}
        self.assertIn("email_seeker@example.com", recipients)
        self.assertIn("Application Received", recipients["email_seeker@example.com"].subject)
        self.assertIn("email_emp@example.com", recipients)
        self.assertIn("New Application Received", recipients["email_emp@example.com"].subject)

        # 2. Status update -> Status Update email to applicant with evaluation note
        mail.outbox.clear()
        self.client.force_authenticate(user=self.emp_user)
        res_status = self.client.patch(
            f"/api/applications/{app_uuid}/status/",
            {"status": "shortlisted", "notes": "Strong distributed systems background"},
        )
        self.assertEqual(res_status.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        status_email = mail.outbox[0]
        self.assertEqual(status_email.to, ["email_seeker@example.com"])
        self.assertIn("Shortlisted", status_email.subject)
        self.assertIn("Strong distributed systems background", status_email.body)

        # 3. Schedule interview -> Single email with RFC 5545 .ics calendar attachment
        mail.outbox.clear()
        res_interview = self.client.post("/api/interviews/", {
            "application": app_uuid,
            "scheduled_at": "2026-12-15T14:30:00Z",
            "mode": "virtual",
            "meeting_link": "https://meet.jobcrest.com/room-42",
            "interview_notes": "System design round",
        })
        self.assertEqual(res_interview.status_code, status.HTTP_201_CREATED)
        interview_uuid = res_interview.data["id"]

        self.assertEqual(len(mail.outbox), 1)
        invite_email = mail.outbox[0]
        self.assertEqual(invite_email.to, ["email_seeker@example.com"])
        self.assertIn("Interview Invitation", invite_email.subject)
        self.assertEqual(len(invite_email.attachments), 1)

        filename, ics_content, mimetype = invite_email.attachments[0]
        self.assertEqual(filename, "interview-invite.ics")
        self.assertIn("text/calendar", mimetype)
        self.assertIn("BEGIN:VCALENDAR", ics_content)
        self.assertIn("METHOD:REQUEST", ics_content)
        self.assertIn("BEGIN:VEVENT", ics_content)
        self.assertIn("DTSTART:20261215T143000Z", ics_content)
        self.assertIn("DTEND:20261215T153000Z", ics_content)
        self.assertIn("ATTENDEE;CN=Email Seeker;RSVP=TRUE:mailto:email_seeker@example.com", ics_content)
        self.assertIn("END:VCALENDAR", ics_content)

        # 4. Reschedule interview -> Rescheduled email with updated .ics
        mail.outbox.clear()
        res_reschedule = self.client.patch(
            f"/api/interviews/{interview_uuid}/",
            {"scheduled_at": "2026-12-16T16:00:00Z"},
        )
        self.assertEqual(res_reschedule.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Interview Rescheduled", mail.outbox[0].subject)
        self.assertIn("DTSTART:20261216T160000Z", mail.outbox[0].attachments[0][1])

        # 5. Withdraw -> Application Withdrawn email to employer
        mail.outbox.clear()
        self.client.force_authenticate(user=self.seeker_user)
        res_withdraw = self.client.delete(f"/api/applications/{app_uuid}/")
        self.assertEqual(res_withdraw.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["email_emp@example.com"])
        self.assertIn("Application Withdrawn", mail.outbox[0].subject)
