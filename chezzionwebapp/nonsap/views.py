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
from .models import NonsapIncidentIssue
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Issue, User  # Adjust model imports as per your project
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
    active_issues = issues.filter(Q(status='active') | Q(status='inprogress')).count()
    # active_issues = issues.filter(status='active').count()
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
            # Create a new comment instance
            comment = Comment(
                comment=form.cleaned_data['comment'],  # Assuming `comment` is the form field
                issue=issue,  # Associate the comment with the issue
                commented_by=request.user  # Associate the comment with the logged-in user
            )
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

def issue_details(request, issue_id):
    issue = Issue.objects.get(id=issue_id)
    attachments = Attachment.objects.filter(issue=issue)
    comments = Comment.objects.filter(issue=issue)
    form = CommentForm(request.POST or None)
    
    return render(request, 'issue-status.html', {
        'issue': issue,
        'attachments': attachments,
        'comments': comments,
        'form': form
    })



def super_admin_page(request):
    if request.user.is_authenticated and request.user.is_superuser:
        issues = IncidentIssue.objects.all()  # Fetch all incident issues
        
        return render(request, 'master/superadmin_dashboard.html', {'issues': issues})
    else:
        return render(request, 'master/superadmin_dashboard.html')
from django.shortcuts import render
from django.db.models import F

def superadmin_dashboard(request):
    if request.user.is_authenticated and request.user.is_superuser:
        issues = (
            IncidentIssue.objects.select_related('reporter')  # Assuming reporter is a ForeignKey
            .annotate(reporter_name=F('reporter__username'))  # Add reporter name to the queryset
            .all()
        )
        # Exclude the superuser from the staff list
        staff_members = User.objects.filter(is_staff=True).exclude(is_superuser=True)
        
        context = {
            'user': request.user,
            'issues': issues,
            'staff_members': staff_members,
        }
        return render(request, 'master/superadmin_dashboard.html', context)
    else:
        return render(request, 'master/access_denied.html')
  # Optional: a dedicated denied access page


def issue_list(request):
    # Get all issues
    issues = Issue.objects.all()

    # Get all staff users
    staff_users = User.objects.filter(is_staff=True)

    # Create a list of dictionaries to hold each issue with its assigned_to_id
    issues_with_assigned_to = []
    for issue in issues:
        assigned_to_id = issue.assigned_to.id if issue.assigned_to else None
        issues_with_assigned_to.append({
            'issue': issue,
            'assigned_to_id': assigned_to_id
        })

    return render(request, 'master/superadmin_dashboard.html', {
        'issues': issues_with_assigned_to,
        'staff_users': staff_users,
    })


@login_required
def assign_issue(request, issue_id):
    if request.method == "POST":
        staff_id = request.POST.get("staff_id")
        issue = get_object_or_404(Issue, id=issue_id)
        staff_member = get_object_or_404(User, id=staff_id, is_staff=True)

        # Assign the issue to the selected staff member
        issue.assigned_to = staff_member
        issue.save()

        # Redirect back to the issue list or display a success message
        return redirect('master/superadmin_dashboard.html')  # Replace with your issue list URL


# @login_required
# def staff_dashboard(request):
#     if not request.user.is_staff:
#         return redirect('home')  # Redirect non-staff users

#     # Fetch issues assigned to the logged-in staff member
#     assigned_issues = Issue.objects.filter(assigned_to=request.user)

#     return render(request, 'admin/admin-dashboard.html', {'assigned_issues': assigned_issues})




def assign_staff(request, issue_id):
    issue = get_object_or_404(IncidentIssue, id=issue_id)

    if request.method == 'POST':
        if staff_id := request.POST.get('staff_id'):
            staff_member = get_object_or_404(User, id=staff_id)
            # Assign the staff member to the issue
            issue.assigned_to = staff_member
            issue.save()

            # Optionally, you can redirect to a success page or back to the issue list
            return redirect('nonsap:view_status', issue_id=issue.id)

    # If not a POST request, just render the page (GET)
    return redirect('nonsap:superadmin_dashboard')  # Or any other fallback page





from django.shortcuts import render, redirect
from django.core.paginator import Paginator

def assigned_complaints(request):
    # Check if the user is authenticated and is a staff member
    if request.user.is_authenticated and request.user.is_staff:
        # Fetch issues assigned to the logged-in staff member
        assigned_issues = IncidentIssue.objects.filter(assigned_to_id=request.user.id)
        
        # Debugging: Print the assigned issues for confirmation
        print("Assigned Issues:", assigned_issues)
        
        # Paginate the issues: Show 10 issues per page
        paginator = Paginator(assigned_issues, 10)
        page = request.GET.get('page')  # Get the page number from the query parameters
        issues_page = paginator.get_page(page)  # Get the paginated issues
        
        # Debugging: Print the paginated issues
        print("Paginated Issues:", issues_page)
        
        # Pass the issues to the template
        context = {'assigned_issues': issues_page}
        return render(request, 'admin/view-assigned.html', context)
    
    # If user is not authenticated or not staff, redirect or show access denied
    return render(request, 'access-denied.html')


