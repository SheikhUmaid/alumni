from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    # Auth
    path('register/', views.SignUpView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/update/', views.ProfileUpdateView.as_view(), name='profile_update'),

    # Dashboards
    path('dashboard/student/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('dashboard/alumni/', views.AlumniDashboardView.as_view(), name='alumni_dashboard'),
    path('dashboard/admin/', views.AdminDashboardView.as_view(), name='admin_dashboard'),

    # Jobs
    path('jobs/', views.JobListView.as_view(), name='job_list'),
    path('jobs/create/', views.JobCreateView.as_view(), name='job_create'),
    path('jobs/<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('jobs/<int:pk>/apply/', views.apply_job, name='apply_job'),

    # Mentorship
    path('mentorship/', views.MentorshipListView.as_view(), name='mentorship_list'),
    path('mentorship/create/', views.MentorshipCreateView.as_view(), name='mentorship_create'),

    # Events
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),

    # Admin Actions
    path('verify/user/<int:pk>/', views.verify_user_action, name='verify_user'),
    path('verify/job/<int:pk>/', views.verify_job_action, name='verify_job'),
]
