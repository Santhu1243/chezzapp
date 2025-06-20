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
import logging
from .forms import ChangePasswordForm

# Set up the logger
logger = logging.getLogger(__name__)

from datetime import timedelta
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
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirect based on user role
            if user.is_superuser:
                return redirect("superadmin_dashboard")  # Change this to the actual URL name
            elif user.is_staff:
                return redirect("admin_dashboard")  # Change this to the actual URL name
            else:
                return redirect("home")  # Change this to the actual home URL name
        else:
            error_message = "Invalid username or password."

    else:
        error_message = None

    return render(request, "login.html", {"error_message": error_message})




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

import logging
logger = logging.getLogger(__name__)



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
            login_link = "https://staging.chezzion.com/superadmin-login/"
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
                logger.error(f"Error sending email to reporter: {e}")

            # Get emails of all superadmins and send one email to all of them
            superadmins = User.objects.filter(is_superuser=True)
            superadmin_emails = [admin.email for admin in superadmins]
            print(f"Superadmin emails: {superadmin_emails}")  # Debugging line

            try:
                send_mail(
                    'New Issue Reported',
                    f'A new issue "{incident_issue.issue}" has been reported by {incident_issue.reporter.username}. Complaint Number:  {incident_issue.custom_id}\n\nTo view and manage this issue, please login here: {login_link}',
                    settings.DEFAULT_FROM_EMAIL,
                    superadmin_emails,  # Send to all superadmins at once
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending email to superadmins: {e}")
                logger.error(f"Error sending email to superadmins: {e}")

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





from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q
from .models import IncidentIssue

@login_required
def dashboard_view(request):
    status_filter = request.GET.get('status', 'all')
    priority = request.GET.get('priority', 'all')

    issues = IncidentIssue.objects.filter(reporter=request.user).order_by('-report_date', '-report_time') 

    # Status filtering
    if status_filter == 'active':
        issues = issues.filter(status='active')
    elif status_filter == 'inprogress':
        issues = issues.filter(status='inprogress')
    elif status_filter == 'resolved':
        issues = issues.filter(status='resolved')

    # Priority filtering
    if priority == 'critical':
        issues = issues.filter(Q(status='active') | Q(status='inprogress'), priority='P0')

    # Pagination
    paginator = Paginator(issues, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Stats
    total_issues = IncidentIssue.objects.filter(reporter=request.user).count()
    active_issues = IncidentIssue.objects.filter(reporter=request.user, status='active').count()
    resolved_issues = IncidentIssue.objects.filter(reporter=request.user, status='resolved').count()
    critical_issues = IncidentIssue.objects.filter(reporter=request.user, priority='P0', status__in=['active', 'inprogress']).count()
    inprogress_issues = IncidentIssue.objects.filter(reporter=request.user, status='inprogress').count()


    return render(
        request,
        'incident-management/dashboard.html',
        {
            'username': request.user.username,
            'issues': page_obj,
            'total_issues': total_issues,
            'active_issues': active_issues,
            'resolved_issues': resolved_issues,
            'critical_issues': critical_issues,
            'inprogress_issues': inprogress_issues,
            'status_filter': status_filter,
            'priority': priority
        }
    )






from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import IncidentIssue

@login_required
def superadmin_dashboard(request):
    if not request.user.is_superuser:
        return render(request, 'master/access_denied.html', status=403)

    # Filters
    status_filter = request.GET.get('status', 'all')
    priority = request.GET.get('priority', 'all')

    # Base queryset
    issues = (
        IncidentIssue.objects.select_related('reporter', 'assigned_to')
        .annotate(
            reporter_name=F('reporter__username'),
            assigned_to_name=F('assigned_to__username')
        )
        .order_by('-report_date', '-report_time')
    )

    # Status filtering
    if status_filter == 'active':
        issues = issues.filter(status='active')
    elif status_filter == 'inprogress':
        issues = issues.filter(status='inprogress')
    elif status_filter == 'resolved':
        issues = issues.filter(status='resolved')

    # Priority filtering
    if priority == 'critical':
        issues = issues.filter(priority='P0', status__in=['active', 'inprogress'])

    # Pagination
    paginator = Paginator(issues, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Staff users (non-superuser staff)
    staff_members = User.objects.filter(is_staff=True).exclude(is_superuser=True)
    status_choices = IncidentIssue._meta.get_field('status').choices

    # Stats
    total_issues = IncidentIssue.objects.count()
    active_issues = IncidentIssue.objects.filter(status='active').count()
    resolved_issues = IncidentIssue.objects.filter(status='resolved').count()
    inprogress_issues = IncidentIssue.objects.filter(status='inprogress').count()
    critical_issues = IncidentIssue.objects.filter(priority='P0', status__in=['active', 'inprogress']).count()

    context = {
        'issues': page_obj,
        'staff_members': staff_members,
        'status_choices': status_choices,
        'total_issues': total_issues,
        'active_issues': active_issues,
        'resolved_issues': resolved_issues,
        'inprogress_issues': inprogress_issues,
        'critical_issues': critical_issues,
        'status_filter': status_filter,
        'priority': priority,
    }

    return render(request, 'master/superadmin_dashboard.html', context)




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
                issue.status = 'inprogress'
                issue.assigned_date = now()   
                issue.save()
                # Sending Email to Staff Member
                login_link = "https://staging.chezzion.com/staff-login/"
                staff_subject = 'New Complaint Assigned to You'
                staff_message = f'Hello {staff.username},\n\nYou have been assigned a new complaint (ID: {issue.custom_id}). Please take appropriate action. please log in here {login_link}'
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
    issue.assigned_to = staff  
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



from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.conf import settings

def common_view(request, issue_id, template_name):
    issue = get_object_or_404(IncidentIssue, id=issue_id)
    attachments = issue.attachments.all()
    staff_members = User.objects.filter(is_staff=True).exclude(is_superuser=True)
    status_choices = IncidentIssue._meta.get_field('status').choices
    priority_choices = IncidentIssue._meta.get_field('priority').choices 


    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.issue = issue
            comment.commented_by = request.user

            if form.cleaned_data.get('comment_text') or form.cleaned_data.get('image'):
                comment.save()

                # Send email notification
                send_comment_notification(issue, comment)

        else:
            print("Form errors:", form.errors)

    else:
        form = CommentForm()

    comments = issue.comments.all()
    paginator = Paginator(comments, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        template_name,
        {
            'issue': issue,
            'attachments': attachments,
            'staff_members': staff_members,
            'form': form,
            'comments': comments,
            'page_obj': page_obj,
            'priority_choices': priority_choices,
            'status_choices': status_choices,
        }
    )

def send_comment_notification(issue, comment):
    """Send email notification on new comment"""
    
    subject = f"New Comment on Issue #{issue.id}"
    message = f"""
    A new message has been added by {comment.commented_by.username}:

    "{comment.comment_text}"


    Regards,
    {comment.commented_by.username}
    """
    
    # Fetch recipients
    reporter_email = issue.reporter.email if issue.reporter else None
    superuser_emails = User.objects.filter(is_superuser=True).values_list('email', flat=True)
    assigned_staff_email = issue.assigned_to.email if issue.assigned_to else None

    recipient_list = list(superuser_emails)
    if reporter_email:
        recipient_list.append(reporter_email)
    if assigned_staff_email:
        recipient_list.append(assigned_staff_email)

    # Send email
    if recipient_list:
        send_mail(subject, strip_tags(message), settings.DEFAULT_FROM_EMAIL, recipient_list)


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



from django.utils.timezone import now

@login_required
def update_status(request, issue_id):
    issue = get_object_or_404(IncidentIssue, id=issue_id)

    if not request.user.is_superuser and not request.user.is_staff:
        return HttpResponseForbidden("You do not have permission to update this status.")

    if request.method == "POST":
        new_status = request.POST.get('status')

        if new_status and new_status in dict(STATUS_CHOICES):
            old_status = issue.status
            
            # Update status and timestamp
            if issue.status != new_status:  # Only update timestamp if status changes
                issue.status = new_status
                issue.status_changed_at = now()
                issue.save()

                # Send email notifications
                send_status_change_email(issue, old_status, new_status)

                messages.success(request, f"Status for issue #{issue_id} updated to '{dict(STATUS_CHOICES)[new_status]}'.")
            else:
                messages.info(request, "No changes detected in status.")

        else:
            messages.error(request, "Invalid status value.")

    # Redirect based on user type
    if request.user.is_superuser:
        return redirect('nonsap:view_issue', issue_id=issue.id)
    elif request.user.is_staff:
        return redirect('nonsap:view_details', issue_id=issue.id)

    return redirect('nonsap:home')




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







@login_required
def update_rootcause(request, issue_id):
    issue = get_object_or_404(IncidentIssue, id=issue_id)

    if request.method == 'POST':
        # Get the root cause from the form
        root_cause = request.POST.get('rootcause')

        # Update the root cause field in the database
        issue.root_cause = root_cause
        issue.save()

        # Get the logged-in staff member
        staff_user = request.user

        super_admins = User.objects.filter(is_superuser=True).values_list('email', flat=True)

        # Send email notification
        if super_admins:
            send_mail(
                subject='Root Cause Updated',
                message=f'The root cause for issue {issue.custom_id} has been updated by {staff_user.username}:\n\n{root_cause}',
                from_email='no-reply@chezzion.com',
                recipient_list=list(super_admins),
                fail_silently=False,
            )

        # Redirect to the issue details page
        return redirect('nonsap:view_details', issue_id=issue.id)

    return render(request, 'admin/view-issue.html', {'issue': issue})




from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from .models import IncidentIssue

from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from .models import IncidentIssue

def update_priority(request, issue_id):
    issue = get_object_or_404(IncidentIssue, id=issue_id)

    if request.method == 'POST':
        priority = request.POST.get('priority')
        resolution_days = request.POST.get('days')
        resolution_time = request.POST.get('resolutionTime')
        resolution_date = request.POST.get('resolutionDate')

        try:
            resolution_days = int(resolution_days) if resolution_days else 0
        except ValueError:
            resolution_days = 0

        issue.priority = priority
        issue.resolution_days = resolution_days

        # Update resolutionDate
        if resolution_date:
            try:
                issue.resolutionDate = datetime.strptime(resolution_date, "%Y-%m-%d").date()
            except ValueError:
                issue.resolutionDate = None
        elif resolution_days > 0:
            issue.resolutionDate = now().date() + timedelta(days=resolution_days)
        else:
            issue.resolutionDate = None

        # Debugging prints
        print(f"Priority: {priority}")
        print(f"Resolution Days: {resolution_days}")
        print(f"Resolution Date (Form Input): {resolution_date}")
        print(f"Computed Resolution Date: {issue.resolutionDate}")

        # Update resolutionTime
        if resolution_time:
            try:
                issue.resolutionTime = datetime.strptime(resolution_time, "%H:%M").time()
            except ValueError:
                issue.resolutionTime = None

        print(f"Resolution Time: {issue.resolutionTime}")  # Debugging

        issue.save()

        return redirect('nonsap:view_issue', issue_id=issue.id)

    return render(request, 'master/view-details.html', {'issue': issue})











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



def all_data(request):
    if request.user.is_authenticated and request.user.is_superuser:
        issues = (
            IncidentIssue.objects.select_related('reporter', 'assigned_to')
            .annotate(reporter_name=F('reporter__username'), assigned_to_name=F('assigned_to__username'))
        )
        staff_members = User.objects.filter(is_staff=True).exclude(is_superuser=True)
        status_choices = Issue._meta.get_field('status').choices


        context = {
            'staff_members': staff_members,
            'status_choices': status_choices,
            'issues': issues
        }
        
        return render(request, 'master/all.html', context)
    




# csv import 
import csv
from django.http import HttpResponse
from django.db.models import F
from .models import IncidentIssue  # Ensure you import the model

def export_issues_csv(request):
    if not (request.user.is_authenticated and request.user.is_superuser):
        return HttpResponse("You do not have permission to access this page.", status=403)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="issues.csv"'

    writer = csv.writer(response)
    writer.writerow(['Complaint ID', 'Project Name', 'email', 'Reporter', 'Issue Title', 'Description', 'rootcause', 'priority', 'Status', 'Reported Date', 'Reported Time', 'Assigned To', 'Assigned on'])

    issues = IncidentIssue.objects.select_related('reporter', 'assigned_to')

    for issue in issues:
        writer.writerow([
            issue.custom_id,
            issue.company_name,
            issue.email,
            issue.reporter.username,
            issue.issue,
            issue.description,
            issue.root_cause,
            issue.priority,
            issue.status,
            issue.report_date,
            issue.report_time,
            issue.assigned_to.username if issue.assigned_to else "Unassigned",
            issue.assigned_date if issue.assigned_to else "Unassigned"
        ])

    return response

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        print("FILES RECEIVED:", request.FILES)  # Debugging

        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)  # Delay saving

            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
                
            profile.save()  # Now save the profile
            return redirect('/')

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, "account/profile.html", {
        "profile": profile, 
        "user_form": user_form, 
        "profile_form": profile_form
    })


from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps user logged in
            return redirect('nonsap:profile')
    else:
        form = PasswordChangeForm(request.user)

    # Add Bootstrap class and placeholder to all fields
    placeholders = {
        'old_password': 'Enter current password',
        'new_password1': 'Enter new password',
        'new_password2': 'Confirm new password',
    }

    for name, field in form.fields.items():
        field.widget.attrs.update({
            'class': 'form-control',
            'placeholder': placeholders.get(name, '')
        })

    return render(request, 'account/change_password.html', {'form': form})




import csv
import chardet
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import IncidentIssue
from .forms import IssueUploadForm

def upload_issues(request):
    if request.method == "POST":
        print("File Upload Attempted")
        form = IssueUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            print("Form is valid")
            csv_file = request.FILES['csv_file']
            print(f"Uploaded File: {csv_file.name}, Size: {csv_file.size} bytes")

            # Detect file encoding
            raw_data = csv_file.read()
            detected_encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            csv_file.seek(0)  # Reset file pointer after reading

            try:
                # Decode file using detected encoding
                decoded_file = raw_data.decode(detected_encoding).splitlines()
                reader = csv.reader(decoded_file)

                for row in reader:
                    try:
                        # Convert date formats if needed
                        report_date = convert_date(row[3])
                        assigned_date = convert_date(row[10])
                        resolution_date = convert_date(row[14])

                        # Handle ForeignKey fields properly
                        reporter = get_user(row[7])
                        assigned_to = get_user(row[9])

                        IncidentIssue.objects.create(
                            issue=row[0],
                            description=row[1],
                            email=row[2],
                            report_date=convert_date(row[3]),
                            report_time=convert_time(row[4]),
                            attachment=row[5] if row[5] else None,  
                            root_cause=row[6],
                            reporter=get_user(row[7]) or request.user,
                            status=row[8],
                            assigned_to=assigned_to,
                            assigned_date=assigned_date,
                            custom_id=row[11],
                            priority=row[12],
                            company_name=row[13],
                            resolutionDate=resolution_date
                        )
                    
                    except ValueError as e:
                        print(f"Skipping row due to error: {e}")
                        continue

                return redirect('issue_list')

            except UnicodeDecodeError as e:
                print(f"Failed to decode file with {detected_encoding}: {e}")
                return render(request, 'incident-management/upload_issues.html', {'form': form, 'error': 'Failed to decode the CSV file.'})

    else:
        form = IssueUploadForm()

    return render(request, 'incident-management/upload_issues.html', {'form': form})


def convert_date(date_str):
    """Convert date from DD/MM/YYYY or other formats to YYYY-MM-DD."""
    if not date_str or date_str.strip() == "":
        return None  # Handle empty dates
    
    for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d"):  # Adjust formats as needed
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    print(f" Invalid date format: {date_str}")
    return None  # Return None if no valid format is found


def get_user(user_id):
    """Fetch User object or return None if invalid."""
    if user_id and user_id.isdigit():
        return User.objects.filter(id=int(user_id)).first()
    return None
from datetime import datetime

def convert_time(time_str):
    """Convert time from various formats to HH:MM:SS."""
    if not time_str or time_str.strip() == "":
        return None  # Handle empty values
    
    for fmt in ("%I:%M %p", "%I:%M:%S %p", "%H:%M", "%H:%M:%S"):  # Common time formats
        try:
            return datetime.strptime(time_str, fmt).strftime("%H:%M:%S")
        except ValueError:
            continue
    
    print(f" Invalid time format: {time_str}")
    return None  # Return None if no valid format is found
