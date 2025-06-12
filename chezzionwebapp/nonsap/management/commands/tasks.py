from celery import shared_task
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from .models import IncidentIssue

@shared_task
def check_and_alert_overdue_issues():
    current_time = now()
    overdue_issues = IncidentIssue.objects.filter(status__in=['active', 'inprogress'])
    superuser_emails = list(User.objects.filter(is_superuser=True).exclude(email='').values_list('email', flat=True))

    for issue in overdue_issues:
        report_datetime = datetime.combine(issue.report_date, issue.report_time)
        deadline = report_datetime + timedelta(days=issue.resolution_days)

        if current_time > deadline:
            subject = f"[ALERT] Overdue Issue - ID #{issue.id}"
            message = f"Issue #{issue.id} reported by {issue.reporter} is overdue."
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, superuser_emails)
