from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .forms import IncidentIssueForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import IncidentIssue, Comment
from .forms import CommentForm

# nonsap/views.py

from .models import Issue  # Ensure the name matches exactly

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


@login_required
def raise_issue(request):
    if request.method == 'POST':
        form = IncidentIssueForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the issue object, but don't save it yet
            incident_issue = form.save(commit=False)
            incident_issue.reporter = request.user  # Automatically set the reporter as the logged-in user
            incident_issue.save()  # Save the issue object

            # Send confirmation email to the user who raised the issue
            try:
                send_mail(
                    'Issue Reported Successfully',
                    f'Your issue "{incident_issue.issue}" has been successfully reported.',
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error to the console for debugging
                print(f"Error sending email to reporter: {e}")

            # Send notification emails to all superadmins
            superadmins = User.objects.filter(is_superuser=True)
            for admin in superadmins:
                try:
                    send_mail(
                        'New Issue Reported',
                        f'A new issue "{incident_issue.issue}" has been reported by {incident_issue.reporter.username}.',
                        settings.DEFAULT_FROM_EMAIL,
                        [admin.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    # Log the error to the console for debugging
                    print(f"Error sending email to superadmin {admin.username}: {e}")

            # Use Django messages to give user feedback
            messages.success(request, f'Issue "{incident_issue.issue}" has been reported successfully!')

            # Redirect after successful form submission
            return redirect('nonsap:success', issue_id=incident_issue.id)  # Make sure you have this URL in your urls.py

        else:
            # If the form is not valid, return with error messages
            messages.error(request, 'There was an error with your form submission. Please try again.')
    else:
        form = IncidentIssueForm()  # Get an empty form for GET requests

    return render(request, 'incident-management/raise-issue.html', {'form': form})



def success(request, issue_id):
    return render(request, 'incident-management/success.html', {'issue_id': issue_id})

@login_required
def viewassigned(request):
    return render(request, 'admin/view-assigned.html')




# @login_required
# def user_issues(request):
#     # Fetch the issues reported by the logged-in user
#     issues = IncidentIssue.objects.filter(reporter=request.user)
#     return render(request, 'incident-management/dashboard.html', {'issues': issues})





@login_required
def dashboard_view(request):
    # Fetch issues reported by the logged-in user
    issues = IncidentIssue.objects.filter(reporter=request.user)
    paginator = Paginator(issues, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Count statistics
    total_issues = issues.count()
    active_issues = issues.filter(status='active').count()
    resolved_issues = issues.filter(status='resolved').count()

    # Render template
    return render(
        request,
        'incident-management/dashboard.html',
        {
            'username': request.user.username,
            'issues': page_obj,
            'total_issues': total_issues,
            'active_issues': active_issues,
            'resolved_issues': resolved_issues,
        }
    )




from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import IncidentIssue
from .forms import CommentForm

@login_required
def view_status(request, issue_id):
    # Fetch the issue object based on the issue_id
    issue = get_object_or_404(IncidentIssue, id=issue_id)

    # Fetch the attachments related to the issue (assuming a related name "attachments")
    attachments = issue.attachments.all()

    # Handle the comment form submission
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.issue = issue
            comment.commented_by = request.user
            comment.save()
    else:
        form = CommentForm()

    # Fetch the comments related to the issue (assuming a related name "comments")
    comments = issue.comments.all()

    return render(
        request,
        'incident-management/issue-status.html',
        {
            'issue': issue,
            'attachments': attachments,
            'form': form,
            'comments': comments,
        }
    )



    