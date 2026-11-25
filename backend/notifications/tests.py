import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model

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
