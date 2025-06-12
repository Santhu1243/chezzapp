from django.core.management.base import BaseCommand
from django.utils.timezone import now, make_aware
from django.core.mail import send_mail
from django.contrib.auth.models import User
from datetime import datetime
from nonsap.models import IncidentIssue  

class Command(BaseCommand):
    help = 'Send alert emails for unresolved issues past their resolution time'

    def handle(self, *args, **kwargs):
        current_time = now()
        issues = IncidentIssue.objects.filter(
            status__in=['active', 'inprogress'],
            alert_sent=False
        )

        overdue_issues = []

        for issue in issues:
            resolution_datetime = make_aware(datetime.combine(issue.resolutionDate, issue.resolutionTime))
            if current_time > resolution_datetime:
                overdue_issues.append(issue)

        if overdue_issues:
            superusers = User.objects.filter(is_superuser=True, email__isnull=False)

            for user in superusers:
                send_mail(
                    subject='🚨 Overdue Incident Issues',
                    message="The following incident issues are overdue:\n" +
                            "\n".join([f"{i.custom_id} - {i.issue}" for i in overdue_issues]),
                    from_email='admin@yourdomain.com',
                    recipient_list=[user.email],
                    fail_silently=False,
                )

            # Mark issues as alerted
            for issue in overdue_issues:
                issue.alert_sent = True
                issue.save()

            self.stdout.write(self.style.SUCCESS(f"Sent alerts for {len(overdue_issues)} issues."))
        else:
            self.stdout.write("✅ No overdue unresolved issues found.")
