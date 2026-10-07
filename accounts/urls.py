from django.urls import path
from . import views

urlpatterns={
    #Auth
    path('auth/register/',views.register_view,name='register'),
    path('auth/login/',views.login_view,name='login'),
    path('auth/logout/',views.logout_view,name='logout'),
    path('auth/me',views.me_view,name='me'),
    path('auth/password-reset/', views.password_reset_request_view, name='password-reset'),
    path('auth/password-reset-confirm/',views.password_reset_confirm_view,name='password-reset-confirm'),

    # JobSeeker profile
    path('jobseeker/profile/', views.jobseeker_profile_view, name='jobseeker-profile'),
    path('jobseeker/profile/resume/', views.jobseeker_resume_upload_view, name='jobseeker-resume-upload'),
    path('jobseeker/profile/<int:id>', views.public_jobseeker_profile_view, name='jobseeker-public-profile'),

    #Education
    path('jobseeker/education/',views.education_list_create_view,name='education-list-create'),
    path('jobseeker/education/<int:pk>/', views.education_detail_view, name='education-detail'),

    #Experience 
    path('jobseeker/experience/', views.experience_list_create_view, name='experience-list-create'),
    path('jobseeker/experience/<int:pk>/', views.experience_detail_view, name='experience-detail'),

    #Skills
    path('jobseeker/skills/',views.skill_list_create_view,name='skills-list-create'),
    path('jobseeker/skills/<int:pk>/',views.skill_list_create_view,name='skills-list-create'),
    path('skills/',views.all_skills_list_view,name='all-skills')
    }   

