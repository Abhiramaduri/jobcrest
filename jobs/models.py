from django.db import models
from django.utils.text import slugify
from companies.models import Company, EmployerProfile
from accounts.models import Skill


class JobCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Job(models.Model):
    JOB_TYPE_CHOICE = (
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('internship', 'Internship'),
        ('contract', 'Contract'),
        ('remote', 'Remote'),
    )
    STATUS_CHOICE = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('expired', 'Expired'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    posted_by = models.ForeignKey(EmployerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='posted_jobs')
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    description = models.TextField()
    responsibilities = models.TextField()
    requirements = models.TextField(blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICE)
    experience_min = models.PositiveBigIntegerField(default=0)
    experience_max = models.PositiveBigIntegerField(null=True, blank=True)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salary_currency = models.CharField(max_length=10, default='INR')
    location = models.CharField(max_length=255, blank=True)
    is_remote = models.BooleanField(default=False)
    skill_required = models.ManyToManyField(Skill, blank=True, related_name='jobs')
    vacancies = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='draft')
    application_deadline = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.company.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class SavedJob(models.Model):
    jobseeker = models.ForeignKey('accounts.JobSeekerProfile', on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('jobseeker', 'job')

    def __str__(self):
        return f"{self.jobseeker} saved {self.job}"
    