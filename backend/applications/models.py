from django.db import models
from jobs.models import Job
from accounts.models import JobSeekerProfile, User
from accounts.validators import validate_resume_file
import uuid


class Application(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('shortlised', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
        ('withdrawn', 'Withdrawn'),
    )
    ALLOWED_STATUS_TRANSITIONS = {
        'applied': ('under_review', 'shortlisted', 'interview_scheduled', 'rejected', 'hired'),
        'under_review': ('shortlisted', 'interview_scheduled', 'rejected', 'hired'),
        'shortlisted': ('interview_scheduled', 'rejected', 'hired'),
        'shortlised': ('interview_scheduled', 'rejected', 'hired'),
        'interview_scheduled': ('rejected', 'hired'),
        'rejected': (),
        'hired': (),
        'withdrawn': (),
    }
    WITHDRAWABLE_STATUSES = (
        'applied',
        'under_review',
        'shortlisted',
        'shortlised',
        'interview_scheduled',
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='application_resumes/', blank=True, null=True, validators=[validate_resume_file])
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f"{self.applicant} -> {self.job}"


class ApplicationStatusHistory(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='history')
    old_status = models.CharField(max_length=30, blank=True)
    new_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.application} : {self.old_status} -> {self.new_status}"


class Interview(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    MODE_CHOICE = (
        ('online', 'Online'),
        ('virtual', 'Virtual'),
        ('in-person', 'In Person'),
        ('in_person', 'In Person'),
        ('phone', 'Phone'),
    )

    RESULT_CHOICES = (
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
    )

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    scheduled_at = models.DateTimeField()
    mode = models.CharField(max_length=20, choices=MODE_CHOICE)
    meeting_link = models.CharField(max_length=500, blank=True)
    interview_notes = models.TextField(blank=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='pending')

    def __str__(self):
        return f"Interview for {self.application}"