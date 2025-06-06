from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from nonsap.models import IncidentIssue
from django.conf import settings

class Command(BaseCommand):
    help = 'Check for unresolved issues older than 2 minutes and send email alerts'

    def handle(self, *args, **kwargs):
        threshold_time = now() - timedelta(minutes=2)
        unresolved_issues = IncidentIssue.objects.filter(status='active', created_at__lte=threshold_time)

        if unresolved_issues.exists():
            superadmins = User.objects.filter(is_superuser=True)
            superadmin_emails = [admin.email for admin in superadmins]

            for issue in unresolved_issues:
                try:
                    send_mail(
                        subject='Unresolved Issue Alert',
                        message=f'The issue "{issue.issue}" (ID: {issue.id}) has not been resolved within 2 minutes.',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=superadmin_emails,
                        fail_silently=False
                    )
                    self.stdout.write(self.style.SUCCESS(f'Alert sent for issue {issue.custom_id}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to send alert for issue {issue.custom_id}: {e}'))
        else:
            self.stdout.write('No unresolved issues older than 2 minutes found.')
