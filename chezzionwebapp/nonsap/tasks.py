from celery import shared_task
from django.utils.timezone import now
from .models import IncidentIssue
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings  # <--- import settings

@shared_task
def check_and_alert_overdue_issues():
    """
    Checks for P0 (critical) issues not updated within 15 minutes and sends alert emails to all superusers.
    """
    critical_issues = IncidentIssue.objects.filter(priority='P0', status='Open')

    for issue in critical_issues:
        if issue.created_at and (now() - issue.created_at).total_seconds() > 900:  # 15 minutes
            # Send alert email to all superusers
            superusers = User.objects.filter(is_superuser=True)
            for superuser in superusers:
                send_mail(
                    subject='[CRITICAL] P0 Issue Unresolved Alert',
                    message=(
                        f"A critical P0 issue (ID: {issue.id}) created at {issue.created_at} "
                        f"has not been resolved within 15 minutes.\n\n"
                        f"Issue Description: {issue.description}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,  # <--- use from settings
                    recipient_list=[superuser.email],
                    fail_silently=False,
                )
