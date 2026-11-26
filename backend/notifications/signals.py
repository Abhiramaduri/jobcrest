from django.db.models.signals import post_save
from django.dispatch import receiver

from applications.models import ApplicationStatusHistory
from .services import notify_for_status_history


@receiver(post_save, sender=ApplicationStatusHistory)
def create_notification_on_status_history(sender, instance, created, **kwargs):
    """Automatically creates user notifications whenever an application status history event is logged."""
    if not created:
        return
    notify_for_status_history(instance)
