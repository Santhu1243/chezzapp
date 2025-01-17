from django.db import models
from django.contrib.auth.models import User

class IncidentIssue(models.Model):
    issue = models.CharField(max_length=255)
    description = models.TextField()
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    report_date = models.DateField()
    report_time = models.TimeField()
    attachment = models.FileField(upload_to='media/', null=True, blank=True)
    root_cause = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.issue
