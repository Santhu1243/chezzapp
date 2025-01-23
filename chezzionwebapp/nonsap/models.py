from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone

# Define STATUS_CHOICES before referencing it in the model
STATUS_CHOICES = [
    ('active', 'Active'),
    ('inprogress', 'inprogress'),
    ('resolved', 'Resolved'),
]

class IncidentIssue(models.Model):
    issue = models.CharField(max_length=255)
    description = models.TextField()
    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reported_issues'
    )
    email = models.EmailField()
    report_date = models.DateField()
    report_time = models.TimeField()
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_date = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='uploads/', null=True, blank=True)
    root_cause = models.TextField(default="No root cause provided")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
    )

    def __str__(self):
        return self.issue



class IncidentIssueForm(forms.ModelForm):
    class Meta:
        model = IncidentIssue
        fields = ['issue', 'description', 'email', 'report_date', 'report_time', 'attachment']


class Issue(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    reported_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
class Meta:
        db_table = 'nonsap_incidentissue'




class Comment(models.Model):
    issue = models.ForeignKey(IncidentIssue, on_delete=models.CASCADE, related_name='comments')
    comment_text = models.TextField()
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE)
    commented_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.commented_by} on {self.commented_at}"


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_text']

class IssueImage(models.Model):
    issue = models.ForeignKey(IncidentIssue, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='issue_images/')
    # other fields
class Attachment(models.Model):
    issue = models.ForeignKey(IncidentIssue, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

from django.db import models
from django.contrib.auth.models import User

class NonsapIncidentIssue(models.Model):
    issue = models.CharField(max_length=255)
    description = models.TextField()
    email = models.EmailField()
    report_date = models.DateField()
    report_time = models.TimeField()
    attachment = models.FileField(upload_to='uploads/', null=True, blank=True)
    root_cause = models.TextField()
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User table
    status = models.CharField(max_length=50)
