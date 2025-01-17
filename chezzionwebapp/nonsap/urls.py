from django.urls import path, include
from .views import authView, home, dashboard_view, logout_view
from . import views

app_name = 'nonsap'
urlpatterns = [
    path("", home, name="home"), 
    path('superadmin/', views.superadmin_dashboard, name='superadmin_dashboard'), 
    path("register/", authView, name="register"),  
    path('accounts/', include('django.contrib.auth.urls')),  
    path('accounts/logout/', logout_view, name='logout'),
    path('incident-management/dashboard/', dashboard_view, name='dashboard'),
    path('staff-admin/admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),  
    path('incident-management/raise-issue/', views.raise_issue, name='raise-issue'),
    path('incident-management/success/<int:issue_id>/', views.success, name='success'),
    path('staff-admin/view-assigned/', views.viewassigned, name='viewassigned'),
    path('incident-management/status/', views.issuestatus, name='issuestatus'),
  
]

