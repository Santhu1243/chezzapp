from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .forms import IncidentIssueForm

# Home view
@login_required
def home(request):
    return render(request, 'home.html')

# Welcome view
@login_required
def welcome_view(request):
    return render(request, 'home.html', {'username': request.user.username})

# Sign-up view
def authView(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login page after successful signup
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

# Logout view
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')  # Ensure 'login' URL exists in urls.py

# Login form class
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

# Login view
def login_view(request):
    if request.user.is_authenticated:
        return redirect(get_redirect_url(request.user))  # Redirect authenticated users

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(get_redirect_url(user))
        else:
            form.add_error(None, "Invalid username or password")
    
    return render(request, 'registration/login.html', {'form': form})

# Helper function for determining redirection URL
def get_redirect_url(user):
    if user.is_superuser:
        return '/superadmin/'  # Superadmin dashboard URL
    elif user.is_staff:
        return '/admin_dashboard/'  # Admin dashboard URL
    else:
        return '/home/'  # Regular user home page

# Dashboard view
@login_required
def dashboard_view(request):
    return render(request, 'incident-management/dashboard.html', {'username': request.user.username})

@login_required
def admin_dashboard(request):
    return render(request, 'admin/admin-dashboard.html')

# Superadmin check
def is_superadmin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superadmin, login_url='login')  # Specify login_url for unauthorized access
def superadmin_dashboard(request):
    return render(request, 'master/superadmin_dashboard.html', {})

# Incident Issue form handling view
# Incident Issue form handling view
@login_required
def raise_issue(request):
    if request.method == 'POST':
        form = IncidentIssueForm(request.POST, request.FILES)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.reporter = request.user  # Automatically set the reporter as the logged-in user
            issue.save()

            # Send email to the logged-in user
            try:
                send_mail(
                    'Issue Reported Successfully',
                    f'Your issue "{issue.issue}" has been successfully reported.',
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending email to reporter: {e}")

            # Send email to superadmins
            superadmins = User.objects.filter(is_superuser=True)
            for admin in superadmins:
                try:
                    send_mail(
                        'New Issue Reported',
                        f'A new issue "{issue.issue}" has been reported by {issue.reporter.username}.',
                        settings.DEFAULT_FROM_EMAIL,
                        [admin.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Error sending email to superadmin {admin.username}: {e}")

            return redirect('success')  # Ensure 'success' URL exists in urls.py
    else:
        form = IncidentIssueForm()
    return render(request, 'incident-management/raise-issue.html', {'form': form})


@login_required
def success(request):
    return render(request, 'incident-management/success.html')

@login_required
def viewassigned(request):
    return render(request, 'admin/view-assigned.html')

@login_required
def issuestatus(request):
    return render(request, 'incident-management/issue-status.html')