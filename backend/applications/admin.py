from django.contrib import admin
from .models import Application,ApplicationStatusHistory,Interview

# Register your models here.
admin.site.register(Application)
admin.site.register(ApplicationStatusHistory)
admin.site.register(Interview)
