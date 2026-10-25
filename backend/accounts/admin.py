from django.contrib import admin
from .models import User, JobSeekerProfile, Skill, JobSeekerSkill, Education, Experience

# Register your models here.
admin.site.register(User)
admin.site.register(JobSeekerProfile)
admin.site.register(Skill)
admin.site.register(Education)
admin.site.register(Experience)

