from django.db import models
from accounts.models import User


class Notification(models.Model):
    TYPE_CHOICE = (
        ('application_update', 'Application Update'),
        ('new_job_match', 'New Job Match'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('general', 'General'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICE, default='general')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

