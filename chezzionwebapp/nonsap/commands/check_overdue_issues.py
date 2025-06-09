from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime, timedelta
from incident.models import IncidentIssue

class Command(BaseCommand):
    help = 'Check and alert superusers for overdue issues'

    def handle(self, *args, **kwargs):
        current_time = now()
        overdue_issues = IncidentIssue.objects.filter(status__in=['active', 'inprogress'])
        superuser_emails = list(User.objects.filter(is_superuser=True).exclude(email='').values_list('email', flat=True))

        if not superuser_emails:
            self.stdout.write(self.style.WARNING("No superusers found with email addresses."))
            return

        for issue in overdue_issues:
            report_datetime = datetime.combine(issue.report_date, issue.report_time)
            deadline = report_datetime + timedelta(days=issue.resolution_days)

            if current_time > deadline:
                subject = f"[ALERT] Overdue Issue - ID #{issue.id}"
                message = (
                    f"The following issue is overdue:\n\n"
                    f"Issue ID: {issue.id}\n"
                    f"Category: {issue.issue}\n"
                    f"Description: {issue.description}\n"
                    f"Priority: {issue.priority}\n"
                    f"Reported by: {issue.reporter.username}\n"
                    f"Report Date: {issue.report_date} {issue.report_time}\n"
                    f"Resolution Deadline: {deadline.strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"Please take necessary action."
                )

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,  # ✅ used from settings
                    superuser_emails,
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f"Alert sent for overdue issue ID #{issue.id}"))
