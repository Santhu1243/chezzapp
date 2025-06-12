from celery import shared_task
from django.utils.timezone import now, make_aware
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from .models import IncidentIssue

@shared_task
def check_and_alert_overdue_issues():
    current_time = now()
    overdue_issues = IncidentIssue.objects.filter(
        status__in=['active', 'inprogress'],
        alert_sent=False
    )
    superuser_emails = list(
        User.objects.filter(is_superuser=True, email__isnull=False)
        .exclude(email='')
        .values_list('email', flat=True)
    )

    for issue in overdue_issues:
        try:
            report_datetime = make_aware(datetime.combine(issue.report_date, issue.report_time))
            deadline = report_datetime + timedelta(days=issue.resolution_days)

            if current_time > deadline:
                subject = f"[ALERT] Overdue Issue - ID #{issue.custom_id}"
                message = (
                    f"Issue #{issue.custom_id} reported by {issue.reporter} is overdue.\n"
                    f"Issue: {issue.issue}\n"
                    f"Reported on: {report_datetime.strftime('%Y-%m-%d %H:%M')}"
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, superuser_emails)

                issue.alert_sent = True
                issue.save()

        except Exception as e:
            print(f"Error processing issue #{issue.id}: {e}")
