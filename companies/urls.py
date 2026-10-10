from django.urls import path
from. import views

urlpatterns=[
    path('companies/',views.company_list_create_view,name='company-list-create'),
    path('companies/<slug:slug>/',views.company_detail_view,name='company-detail'),
    # path('companies/<slug:slug>/jobs/', views.company_jobs_view, name='company-jobs'),
    path('companies/<slug:slug>/recruiters/',views.company_recruiters_view,name='company-recruiters'),
    path('employers/profile/',views.employer_profile_view,name='employer-profile')
]