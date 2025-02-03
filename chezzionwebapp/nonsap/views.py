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
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Issue, User 
from .models import Issue  
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from .models import Attachment
from django.urls import path
from .models import IncidentIssue, User
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.db.models import F
from .forms import StaffLoginForm, SuperAdminLoginForm
from django.shortcuts import redirect
from django.contrib.auth.models import Group

# Home view
@login_required
def home(request):
    return render(request, 'home.html')


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
def logout_view(request):
    # Check if the user is superuser, staff, or regular user
    if request.user.is_superuser:
        logout(request)
        return redirect('superadmin_login')  # Redirect to superuser dashboard
    elif request.user.is_staff:
        logout(request)
        return redirect('staff_login')  # Redirect to staff dashboard
    else:
        logout(request)
        return redirect('login')# Ensure 'login' URL exists in urls.py

# Login form class
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


def authenticate_user(request, username, password):
    user = authenticate(request, username=username, password=password)
    if user is not None:
        print(f"Authenticated user: {user.username}")  # Debugging
        login(request, user)
        return redirect(get_redirect_url(user))
    return None


# Login viewfrom django.contrib import messages




def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Get the user credentials from the form
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Authenticate the user
            user = authenticate(request, username=username, password=password)
            
            if user is None:
                # If authentication fails, return an error
                form.add_error(None, "Invalid username or password.")
            elif user.is_staff or user.is_superuser:
                # Add an error message if the user is staff or superuser
                form.add_error(None, "Access denied. Only regular users are allowed.")
            else:
                # Log the user in
                login(request, user)
                messages.success(request, f"Logged in as {user.username}")
                
                # Redirect to home page or another page
                return redirect('home')  # Replace 'home' with your desired URL name
        else:
            form.add_error(None, "Please fill in all fields.")
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})



# Helper function for determining redirection URLimport logging

from django.urls import reverse

def get_redirect_url(user):
    if user.is_superuser:
        return reverse('superadmin_dashboard')  # assuming you have a named URL
    elif user.is_staff:
        return reverse('admin_dashboard')
    else:
        return reverse('home')




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
        files = request.FILES.getlist('attachment')  # Get all uploaded files
        if form.is_valid():
            # Create the issue object and save it
            incident_issue = form.save(commit=False)
            incident_issue.reporter = request.user
            incident_issue.save()

            # Save the attachments in the `nonsap_attachment` table
            for file in files:
                Attachment.objects.create(
                    file=file,  # Store the file name
                    issue_id=incident_issue.id,  # Link the attachment to the issue
                    uploaded_at=now()
                )

            # Send email notification to the reporter
            try:
                send_mail(
                    'Issue Reported Successfully',
                    f'Your issue "{incident_issue.issue}" has been successfully reported. We will send you an email once it is resolved.',
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending email to reporter: {e}")

            # Get emails of all superadmins and send one email to all of them
            superadmins = User.objects.filter(is_superuser=True)
            superadmin_emails = [admin.email for admin in superadmins]

            try:
                send_mail(
                    'New Issue Reported',
                    f'A new issue "{incident_issue.issue}" has been reported by {incident_issue.reporter.username}. Complaint Number:  {incident_issue.reporter.custom_id}',
                    settings.DEFAULT_FROM_EMAIL,
                    superadmin_emails,  # Send to all superadmins at once
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending email to superadmins: {e}")

            # Success message and redirect
            messages.success(request, f'Issue "{incident_issue.issue}" has been reported successfully!')
            return redirect('nonsap:success', issue_id=incident_issue.id)

        else:
            messages.error(request, 'There was an error with your form submission. Please try again.')
    else:
        form = IncidentIssueForm()

    return render(request, 'incident-management/raise-issue.html', {'form': form})



def success(request, issue_id):
    issue = get_object_or_404(IncidentIssue, id=issue_id)
    return render(request, 'incident-management/success.html', {'issue': issue})







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







def superadmin_dashboard(request):
    if request.user.is_authenticated and request.user.is_superuser:
        issues = (
            IncidentIssue.objects.select_related('reporter', 'assigned_to')
            .annotate(reporter_name=F('reporter__username'), assigned_to_name=F('assigned_to__username'))
        )
        staff_members = User.objects.filter(is_staff=True).exclude(is_superuser=True)
        status_choices = Issue._meta.get_field('status').choices

        # Pagination logic
        paginator = Paginator(issues, 10)  # Show 10 issues per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'issues': page_obj,
            'staff_members': staff_members,
            'status_choices': status_choices,
        }
        
        return render(request, 'master/superadmin_dashboard.html', context)
    
    return render(request, 'master/access_denied.html', status=403)


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





from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import IncidentIssue, User

@login_required
def assign_staff(request, issue_id):  # sourcery skip: use-named-expression
    try:
        issue = IncidentIssue.objects.get(id=issue_id)
    except IncidentIssue.DoesNotExist:
        messages.error(request, 'Issue not found.')
        return redirect('nonsap:superadmin_dashboard')

    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        if staff_id:
            try:
                staff = User.objects.get(id=staff_id, is_staff=True)
                assign_staff_to_issue(staff, issue)  # Assign staff to the issue
                issue.save()

                # Sending Email to Staff Member
                staff_subject = 'New Complaint Assigned to You'
                staff_message = f'Hello {staff.username},\n\nYou have been assigned a new complaint (ID: {issue.custom_id}). Please take appropriate action.'
                send_mail(
                    staff_subject,
                    staff_message,
                    settings.DEFAULT_FROM_EMAIL,  
                    [staff.email],
                    fail_silently=False,
                )

                # Sending Email to User (Reporter)
                user_subject = 'Your Complaint has been Assigned to Staff'
                user_message = f'Hello {issue.reporter.username},\n\nYour complaint {issue.custom_id} has been successfully assigned to {staff.username}. They will reach out to you soon.'
                send_mail(
                    user_subject,
                    user_message,
                    settings.DEFAULT_FROM_EMAIL,  
                    [issue.reporter.email],
                    fail_silently=False,
                )

                messages.success(request, f'Complaint {issue.custom_id} has been successfully assigned to {staff.username}.')
                return redirect('nonsap:superadmin_dashboard')

            except User.DoesNotExist:
                messages.error(request, 'Selected staff member not found.')
                return redirect('nonsap:assign_staff', issue_id=issue_id)
        else:
            messages.error(request, 'Please select a staff member to assign the complaint.')
            return redirect('nonsap:assign_staff', issue_id=issue_id)

    staff_members = User.objects.filter(is_staff=True)
    return render(request, 'master/assign_staff.html', {'issue': issue, 'staff_members': staff_members})


def assign_staff_to_issue(staff, issue):
    # Assign the staff member to the issue
    issue.assigned_to = staff  # Assuming you have an 'assigned_to' field in your model
    issue.save()







def assigned_complaints(request):
    if request.user.is_authenticated and request.user.is_staff:
        assigned_issues = IncidentIssue.objects.filter(assigned_to_id=request.user.id)
        
        # Debugging print statement
        print("Assigned Issues:", assigned_issues)
        
        paginator = Paginator(assigned_issues, 5)  # Paginate the issues
        page = request.GET.get('page')  # Get the page number from the query parameters
        issues_page = paginator.get_page(page)  # Get the paginated issues
        
        # Debugging print statement for paginated issues
        print("Paginated Issues:", issues_page)
        
        context = {'assigned_issues': issues_page}
        return render(request, 'admin/view-assigned.html', context)
    
    return render(request, 'access-denied.html')



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import IncidentIssue, Comment
from .forms import CommentForm
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

def common_view(request, issue_id, template_name):
    # Fetch the issue object
    issue = get_object_or_404(IncidentIssue, id=issue_id)

    # Fetch attachments
    attachments = issue.attachments.all()

    # Handle form submission
    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.issue = issue
            comment.commented_by = request.user
            
            if form.cleaned_data.get('comment_text') or form.cleaned_data.get('image'):
                comment.save()
        else:
            print("Form errors:", form.errors)  # Log errors here if necessary
        
    else:
        form = CommentForm()

    # Fetch comments
    comments = issue.comments.all()

    # Pagination logic
    paginator = Paginator(comments, 5)  # Show 5 comments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        template_name,
        {
            'issue': issue,
            'attachments': attachments,
            'form': form,
            'comments': comments,
            'page_obj': page_obj,  # Include paginated comments
        }
    )

@login_required
def view_details(request, issue_id):
    return common_view(request, issue_id, 'admin/view-issue.html')

@login_required
def view_issue(request, issue_id):
    return common_view(request, issue_id, 'master/view-details.html')

@login_required
def view_status(request, issue_id):
    return common_view(request, issue_id, 'incident-management/issue-status.html')




from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from .models import IncidentIssue, STATUS_CHOICES
from django.shortcuts import get_object_or_404, render


@login_required
def update_status(request, issue_id):
    issue = get_object_or_404(IncidentIssue, id=issue_id)

    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to update this status.")

    if request.method == "POST":
        new_status = request.POST.get('status')

        # Check if the status is valid
        if new_status and new_status in dict(STATUS_CHOICES):
            old_status = issue.status
            issue.status = new_status
            issue.save()

            # Send email notifications for the status change
            send_status_change_email(issue, old_status, new_status)

            messages.success(request, f"Status for issue #{issue_id} updated to '{dict(STATUS_CHOICES)[new_status]}'.")
        else:
            messages.error(request, "Invalid status value.")

    # Check where to redirect after updating the status
    if 'from_dashboard' in request.GET:
        template_name = 'master/superadmin_dashboard.html'
    else:
        template_name = 'master/view-details.html'

    context = {
        'issue': issue,
        'status_choices': STATUS_CHOICES,
    }
    return render(request, template_name, context)


def send_status_change_email(issue, old_status, new_status):
    # Send email to the user (reporter)
    send_mail(
        f'Issue #{issue.id} Status Changed',
        f'Your issue "{issue.issue}" with complaint id : "{issue.custom_id}" has been updated from "{old_status}" to "{new_status}".',
        settings.DEFAULT_FROM_EMAIL,
        [issue.reporter.email],
        fail_silently=False,
    )

    # Send email to the assigned staff if the staff has been assigned
    if issue.assigned_to:
        send_mail(
            f'New Issue Assigned to You: #{issue.custom_id}',
            f'You have been assigned to the issue "{issue.issue}". The status is now "{new_status}".',
            settings.DEFAULT_FROM_EMAIL,
            [issue.assigned_to.email],
            fail_silently=False,
        )



# login pages 

from django.contrib.auth import authenticate, login


# Staff login view
def staff_login_view(request):
    if request.method == 'POST':
        form = StaffLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_staff:
                login(request, user)
                messages.success(request, f"Logged in as staff: {user.username}")
                return redirect('nonsap:admin-dashboard')  # Redirect to staff dashboard
            else:
                messages.error(request, "Invalid username or password, or not authorized.")
    else:
        form = StaffLoginForm()

    return render(request, 'registration/staff_login.html', {'form': form})

# SuperAdmin login view
def superadmin_login_view(request):
    if request.method == 'POST':
        form = SuperAdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_superuser:
                login(request, user)
                messages.success(request, f"Logged in as superadmin: {user.username}")
                return redirect('nonsap:superadmin_dashboard')  # Redirect to superadmin dashboard
            else:
                messages.error(request, "Invalid username or password, or not authorized.")
    else:
        form = SuperAdminLoginForm()

    return render(request, 'registration/superadmin_login.html', {'form': form})





def update_rootcause(request, issue_id):
    issue = get_object_or_404(IncidentIssue, id=issue_id)

    if request.method == 'POST':
        # Get the root cause from the form
        root_cause = request.POST.get('rootcause')

        # Update the root cause field in the database
        issue.root_cause = root_cause
        issue.save()

        # Redirect to the issue details page or another page after update
        return redirect('nonsap:view_details', issue_id=issue.id)

    return render(request, 'admin/view-issue.html', {'issue': issue})


from django.shortcuts import render, get_object_or_404, redirect
from .models import Issue

def update_priority(request, issue_id):
    # Get the issue object
    issue = get_object_or_404(IncidentIssue, id=issue_id)

    if request.method == 'POST':
        # Get the selected priority and resolution days
        priority = request.POST.get('priority')
        resolution_days = request.POST.get('days')

        # Update the priority and resolution days in the database
        issue.priority = priority
        issue.resolution_days = resolution_days
        issue.save()

        # Redirect to the issue detail page or other relevant page
        return redirect('nonsap:view_issue', issue_id=issue.id)

    # If not POST, render the form with the current issue data
    return render(request, 'issue_detail.html', {'issue': issue})






@login_required
def user_redirect(request):
    if request.user.is_superuser:
        return redirect('nonsap:superadmin_dashboard')
    elif request.user.is_staff:
        return redirect('nonsap:admin-dashboard')
    else:
        return redirect('nonsap:home')

from django.contrib.auth.models import User

def get_user_group(self):
    return self.groups.first().name if self.groups.exists() else ""

User.add_to_class("group_name", property(get_user_group))


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile_page(request):
    user = request.user

    # Determine which base template to use
    if user.is_superuser:
        base_template = "superuser-base.html"
    elif user.is_staff:
        base_template = "admin-base.html"
    else:
        base_template = "base.html"

    # Get user's groups
    groups = user.groups.all()

    return render(request, "account/profile.html", {"user": request.user})

