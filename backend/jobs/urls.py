from django.urls import path 
from . import views 

urlpatterns = [
    path('jobs/categories/', views.job_category_list_view, name='job-categories'),
    path('jobs/skills/', views.job_skills_list_view, name='job-skills'),
    path('jobs/my-postings/', views.my_postings_view, name='my-postings'),
    path('jobs/recommended/', views.recommended_jobs_view, name='recommended-jobs'),
    path('jobs/saved/', views.saved_jobs_list_view, name='saved-jobs'),
    path('jobs/', views.job_list_create_view, name='job-list-create'),
    path('jobs/<slug:slug>/save/', views.save_job_view, name='save-jobs'),
    path('jobs/<slug:slug>/unsave/', views.unsave_job_view, name='unsave-job'),
    path('jobs/<slug:slug>/status/', views.job_status_update_view, name='job-status-update'),
    # path('jobs/<slug:slug>/applicants/', views.job_applicants_view, name='job-applicants'),
    path('jobs/<slug:slug>/', views.job_detail_view, name='job-detail'),
]