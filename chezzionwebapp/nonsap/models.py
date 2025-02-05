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
PRIORITY_CHOICES = [
    ('P1', 'P1 - High'),
    ('P2', 'P2 - Medium'),
    ('P3', 'P3 - Low'),
    ('P4', 'P4 - Custom'),
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
    assigned_date = models.DateTimeField(default="2021-09-01 00:00:00")
    attachment = models.FileField(upload_to='uploads/', null=True, blank=True)
    root_cause = models.TextField(default="No root cause provided")
    status = models.CharField(
         max_length=10,
         choices=STATUS_CHOICES,
         default='active',
     )
    priority = models.CharField(
         max_length=10,
         choices=PRIORITY_CHOICES,
         default='active',
     )
    company_name = models.CharField(max_length=255, default="unknown")
    resolutionDate = models.DateField(null=True)
    

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
        fields = ['issue', 'description', 'email', 'report_date', 'report_time', 'attachment', 'company_name', 'resolutionDate', 'priority']


class Issue(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    reported_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    custom_id = models.CharField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    PRIORITY_CHOICES = [
        ('P1', 'P1 - High'),
        ('P2', 'P2 - Medium'),
        ('P3', 'P3 - Low'),
        ('P4', 'P4 - Custom'),
    ]
    priority = models.CharField(max_length=2, choices=PRIORITY_CHOICES, blank=True, null=True)
    custom_days = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return self.title
class Meta:
        db_table = 'nonsap_incidentissue'




class Comment(models.Model):
    issue = models.ForeignKey(IncidentIssue, on_delete=models.CASCADE, related_name='comments')
    comment_text = models.TextField()
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE)
    commented_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='comments/', blank=True, null=True)
    def __str__(self):
        return f"Comment by {self.commented_by} on {self.commented_at}"


from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_text', 'image']  # Add 'image' field

    image = forms.ImageField(required=False)  # Optional image upload



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





class PriorityForm(forms.Form):
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))




from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.username
