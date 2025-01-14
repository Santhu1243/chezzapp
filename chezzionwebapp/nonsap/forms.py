from django import forms
from .models import IncidentIssue

class IncidentIssueForm(forms.ModelForm):
    class Meta:
        model = IncidentIssue
        fields = ['issue', 'description', 'reporter', 'email', 'report_date', 'report_time', 'attachment', 'root_cause']
