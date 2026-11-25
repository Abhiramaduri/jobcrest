from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import uuid
from django.utils import timezone
from datetime import timedelta
from .validators import validate_resume_file


class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    USER_TYPE_CHOICES = (
        ('jobseeker', 'Job Seeker'),
        ('employer', 'Employer'),
        ('admin', 'Admin'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class OTPVerification(models.Model):
    """Stores OTP for email verification and password reset."""
    PURPOSE_CHOICES = (
        ('registration', 'Registration'),
        ('password_reset', 'Password Reset'),
    )
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    @classmethod
    def generate_otp(cls, email, purpose):
        """Delete old OTPs and create a fresh 6-digit one."""
        cls.objects.filter(email=email, purpose=purpose, is_used=False).delete()
        otp_code = str(random.randint(100000, 999999))
        return cls.objects.create(email=email, otp=otp_code, purpose=purpose)

    def __str__(self):
        return f"{self.email} — {self.purpose} — {self.otp}"


class JobSeekerProfile(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='jobseeker_profile')
    full_name = models.CharField(max_length=255)
    headline = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    resume = models.FileField(upload_to='resume/', blank=True, null=True, validators=[validate_resume_file])
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    experience_years = models.PositiveBigIntegerField(default=0)
    current_ctc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    expected_ctc = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    is_open_to_work = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name


class Skill(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class JobSeekerSkill(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    PROFICIENCY_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert'),
    )
    jobseeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, blank=True)

    class Meta:
        unique_together = ('jobseeker', 'skill')

    def __str__(self):
        return f"{self.jobseeker} - {self.skill}"


class Education(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    jobseeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='education')
    degree = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255, blank=True)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveBigIntegerField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    grade = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Experience(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    jobseeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='experience')
    company_name = models.CharField(max_length=255)
    role_title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.role_title} at {self.company_name}"