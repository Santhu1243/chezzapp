from django import forms
from .models import IncidentIssue
from django.contrib.auth.models import User

from django import forms

class IncidentForm(forms.ModelForm):
   
    def clean(self):
        cleaned_data = super().clean()
        priority = cleaned_data.get('priority')
        custom_days = cleaned_data.get('custom_days')

        # Validation for custom days when P4 is selected
        if priority == 'P4' and not custom_days:
            raise forms.ValidationError('Please enter custom days for P4 priority.')

        return cleaned_data
    class Meta:
        model = IncidentIssue
        fields = ['issue', 'description', 'email', 'report_date', 'report_time','priority','resolution_date','attachment', 'root_cause', ]


class IncidentIssueForm(forms.ModelForm):
    class Meta:
        model = IncidentIssue
        fields = ['issue', 'description', 'email', 'report_date', 'report_time','priority','resolution_date','attachment', 'root_cause', ]


    def clean_reporter(self):  # sourcery skip: raise-from-previous-error
        """ Custom validation for the reporter field. """
        reporter_username = self.cleaned_data.get('reporter')
        try:
            reporter_user = User.objects.get(username=reporter_username)  # Get the User object
        except User.DoesNotExist:
            raise forms.ValidationError("The user does not exist.")  # Handle the case where the user does not exist
        return reporter_user

    def save(self, commit=True):
        # Save the form instance but don't save to the database yet
        instance = super().save(commit=False)
        
        # If you need additional custom handling (like saving the `reporter` directly)
        instance.reporter = self.cleaned_data.get('reporter')  # Ensure `reporter` is set as a User instance

        if commit:
            instance.save()  # Save the model to the database

        return instance

from django import forms
from .models import Comment  # Replace with the actual model name

class CommentForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',  # Bootstrap class for textarea styling
            'placeholder': 'Write your comment here...',
            'rows': 4,
        }),
        max_length=500
    )

    def save(self, incident, user, commit=True):
        """
        Save the form data to the database, associating it with an incident and user.
        """
        comment_instance = Comment(
            comment=self.cleaned_data['comment'],
            incident=incident,  
            user=user           
        )
        if commit:
            comment_instance.save()
        return comment_instance

# Staff Login Form
class StaffLoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

# SuperAdmin Login Form
class SuperAdminLoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)