from django.db import models
from django.contrib.auth.models import User
from django import forms

class IncidentIssue(models.Model):
    issue = models.CharField(max_length=255)
    description = models.TextField()
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()  
    report_date = models.DateField()
    report_time = models.TimeField()  # Store time in the database
    attachment = models.FileField(upload_to='uploads/', null=True, blank=True)  # Optional field
    root_cause = models.TextField(default="No root cause provided")  # Add default

    def __str__(self):
        return self.issue

class IncidentIssueForm(forms.ModelForm):
    class Meta:
        model = IncidentIssue
        fields = ['issue']  # Do not include 'reporter' here, it will be automatically set

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the 'reporter' field automatically when saving
        if not self.instance.pk:  # If it's a new instance (not saved yet)
            self.fields['reporter'].initial = None
