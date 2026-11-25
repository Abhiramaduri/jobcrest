"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseForbidden
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import health_check_view

def protected_resume_media_view(request, path):
    return HttpResponseForbidden("Direct access to resume media is prohibited. Use signed expiring links.")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check_view, name='health-check'),
    path('healthz', health_check_view, name='healthz'),
    path('media/resume/<path:path>', protected_resume_media_view),
    path('media/application_resumes/<path:path>', protected_resume_media_view),
    path('api/', include('accounts.urls')), #APP
    path('api/', include('companies.urls')),
    path('api/', include('jobs.urls')),
    path('api/', include('applications.urls')),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token-refresh')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

