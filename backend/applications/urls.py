from django.urls import path
from . import views

urlpatterns = [
    path('application/', views.apply_to_job_view, name='apply-to-job'),
    path('applications/', views.apply_to_job_view, name='apply-to-job-plural'),
    path('applications/apply/', views.apply_to_job_view, name='apply-to-job-alt'),
    path('applications/my-application/', views.my_application_view, name='my-applications'),
    path('applications/my-applications/', views.my_application_view, name='my-applications-plural'),
    path('applications/job/<str:job_id>/', views.applications_by_job_view, name='application-by-job'),
    path('applications/<str:pk>/', views.application_detail_view, name='application-detail'),
    path('aplications/<str:pk>/', views.application_detail_view, name='application-detail-typo-compat'),
    path('applications/<str:pk>/status/', views.application_status_update_view, name='application-status-update'),
    path('applications/<str:pk>/history/', views.application_history_view, name='application-history'),
    path('interviews/', views.interview_create_view, name='interview-create'),
    path('interviews/my-interviews/', views.my_interviews_view, name='my-interviews'),
    path('interviews/employer/', views.employer_interviews_view, name='employer-interviews'),
    path('interviews/<str:pk>/', views.interview_detail_view, name='interview-detail'),
]