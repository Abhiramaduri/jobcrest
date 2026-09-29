from django.db import models
from jobs.models import Job
from accounts.models import JobSeekerProfile,User
# Create your models here.

class Application(models.Model):
    STATUS_CHOICES=(
        ('applied','Applied'),
        ('under_review','Under Review'),
        ('shortlised','Shortlisted'),
        ('interview_scheduled','Interview Scheduled'),
        ('rejected','Rejected'),
        ('hired','Hired')
        )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    cover_letter=models.TextField(blank=True)
    status=models.CharField(max_length=30,choices=STATUS_CHOICES, default='applied')
    applied_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        unique_together=('job','applicant')
    def __str__(self):
        return f"{self.applicant}->{self.job}"

class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='history')
    old_status = models.CharField(max_length=30, blank=True)
    new_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def _str_(self):
        return f"{self.application} : {self.old_status} -> {self.new_status}"
    
    
class Interview(models.Model):
    MODE_CHOICE = (
        ('online', 'Online'),
        ('in-person', 'In Person'),
        ('phone', 'Phone')
    )
    
    RESULT_CHOICES = (
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed')
    )
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    scheduled_at = models.DateTimeField()
    mode = models.CharField(max_length=20, choices=MODE_CHOICE)
    meeting_link = models.CharField(max_length=500, blank=True)
    interview_notes = models.TextField(blank=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='pending')
    
    def _str_(self):
        return f"Interview for {self.application}"