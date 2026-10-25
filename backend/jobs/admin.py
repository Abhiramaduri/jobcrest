from django.contrib import admin
from .models import JobCategory,Job,SavedJob
# Register your models here.
admin.site.register(JobCategory)
admin.site.register(Job)
admin.site.register(SavedJob)
