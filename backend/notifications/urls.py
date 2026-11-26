from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notification_list_view, name='notification-list'),
    path('notifications/unread-count/', views.notification_unread_count_view, name='notification-unread-count'),
    path('notifications/mark-all-read/', views.notification_mark_all_read_view, name='notification-mark-all-read'),
    path('notifications/<str:pk>/read/', views.notification_mark_read_view, name='notification-mark-read'),
]
