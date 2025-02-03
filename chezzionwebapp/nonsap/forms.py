from django import forms
from .models import IncidentIssue, Comment
from django.contrib.auth.models import User


class IncidentIssueForm(forms.ModelForm):
    report_time = forms.TimeField(
        input_formats=['%I:%M %p'],  # Accepts 'hh:mm AM/PM'
        widget=forms.TimeInput(format='%I:%M %p', attrs={'class': 'form-control', 'placeholder': 'hh:mm AM/PM'})
    )

    reporter = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter reporter username'})
    )  # Added to allow user input

    class Meta:
        model = IncidentIssue
        fields = ['issue', 'description', 'email', 'report_date', 'report_time', 'attachment', 'reporter']

    def clean_reporter(self):
        """ Custom validation for the reporter field. """
        reporter_username = self.cleaned_data.get('reporter')
        if not reporter_username:
            raise forms.ValidationError("Reporter username is required.")
        try:
            return User.objects.get(username=reporter_username)  # Return the User object
        except User.DoesNotExist:
            raise forms.ValidationError("The user does not exist.")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.reporter = self.cleaned_data.get('reporter')  # Assign User object to reporter
        if commit:
            instance.save()
        return instance


class CommentForm(forms.ModelForm):
    comment_text = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3})
    )
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={"class": "form-control"}))

    class Meta:
        model = Comment
        fields = ["comment_text", "image"]

    def save(self, commit=True):
        comment_instance = super().save(commit=False)
        if commit:
            comment_instance.save()
            self.save_m2m()
        return comment_instance


# Staff Login Form
class StaffLoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))


# SuperAdmin Login Form
class SuperAdminLoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
