from django.urls import path, include
from .views import authView, home, dashboard_view, logout_view, staff_login_view, superadmin_login_view
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

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
    path('staff-admin/view-assigned/', views.assigned_complaints, name='assigned_complaints'),
    path('incident-management/view-status/<int:issue_id>/', views.view_status, name='view_status'),
    path('superuser/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('superuser/view-issue/<int:issue_id>/', views.view_issue, name='view_issue'),
    path('assign-staff/<int:issue_id>/', views.assign_staff, name='assign_staff'),
    path('staff-admin/viewdetails/<int:issue_id>/', views.view_details, name='view_details'),
    path('update-status/<int:issue_id>/', views.update_status, name='update_status'),
    path('superadmin-login/', views.superadmin_login_view, name='superadmin_login'),
    path('staff-login/', views.staff_login_view, name='staff_login'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
