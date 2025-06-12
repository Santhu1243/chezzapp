from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_profile(sender, instance, **kwargs):
#     instance.profile.save()


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime, timedelta
from .models import IncidentIssue

@receiver(post_save, sender=IncidentIssue)
def alert_if_issue_overdue(sender, instance, created, **kwargs):
    if instance.status in ['active', 'inprogress'] and not instance.alert_sent:
        try:
            # Combine date and time into datetime
            report_datetime = datetime.combine(instance.report_date, instance.report_time)
            deadline = report_datetime + timedelta(days=instance.resolution_days)

            # If current time > deadline, send alert
            if now() > deadline:
                superusers = User.objects.filter(is_superuser=True, email__isnull=False)
                recipient_emails = [user.email for user in superusers]

                send_mail(
                    subject=f"[ALERT] Overdue Issue - ID #{instance.id}",
                    message=f"Issue #{instance.id} reported by {instance.reporter} is overdue.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipient_emails,
                    fail_silently=False,
                )

                instance.alert_sent = True
                instance.save()
        except Exception as e:
            print(f"Error checking overdue issue: {e}")
