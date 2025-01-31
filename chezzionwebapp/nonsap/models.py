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
    custom_id = models.CharField(max_length=255, unique=True, blank=True)
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
    assigned_staff = models.ForeignKey(User, related_name='assigned_issues', on_delete=models.SET_NULL, null=True, blank=True)
    attachment = models.FileField(upload_to='uploads/', null=True, blank=True)
    root_cause = models.TextField(default="No root cause provided")
    status = models.CharField(
         max_length=10,
         choices=STATUS_CHOICES,
         default='active',
     )
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  
        if not self.custom_id:
            self.custom_id = f"CHEZZ-ISSUE-{self.id:05d}"
            super().save(*args, **kwargs)  

    def __str__(self):
        return self.issue
    class Meta:
            db_table = 'nonsap_incidentissue'
   



class IncidentIssueForm(forms.ModelForm):
    class Meta:
        model = IncidentIssue
        fields = ['issue', 'description', 'email', 'report_date', 'report_time', 'attachment']


class Issue(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    reported_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    custom_id = models.CharField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

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


from django import forms

class CommentForm(forms.Form):
    comment_text = forms.CharField(widget=forms.Textarea, required=True)


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

