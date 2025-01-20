from django import forms
from .models import IncidentIssue
from django.contrib.auth.models import User



class IncidentIssueForm(forms.ModelForm):
    report_time = forms.TimeField(
        input_formats=['%I:%M %p'],  # Accepts 'hh:mm AM/PM'
        widget=forms.TimeInput(format='%I:%M %p', attrs={'class': 'form-control', 'placeholder': 'hh:mm AM/PM'})
    )

    class Meta:
        model = IncidentIssue
        fields = ['issue', 'description', 'email', 'report_date', 'report_time', 'attachment', 'root_cause']

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
    comment = forms.CharField(widget=forms.Textarea, max_length=500)

    def save(self, incident, user, commit=True):
        """
        Save the form data to the database, associating it with an incident and user.
        """
        comment_instance = Comment(
            comment=self.cleaned_data['comment'],
            incident=incident,  # Associate the comment with an incident
            user=user           # Associate the comment with the user
        )
        if commit:
            comment_instance.save()
        return comment_instance

