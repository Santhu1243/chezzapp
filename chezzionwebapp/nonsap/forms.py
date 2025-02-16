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
        fields = ['issue', 'description', 'email', 'report_date', 'report_time', 'attachment', 'reporter', 'company_name',  'priority']

    def clean_reporter(self):  # sourcery skip: raise-from-previous-error
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
        required=False,  # Make comment text optional
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3})
    )
    image = forms.ImageField(
        required=False,  # Make image optional
        widget=forms.FileInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Comment
        fields = ["comment_text", "image"]  # Allow both comment and image

    def save(self, commit=True):
        # Save the comment instance
        comment_instance = super().save(commit=False)
        if commit:
            comment_instance.save()  # Save to the database
        return comment_instance



# Staff Login Form
class StaffLoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))


# SuperAdmin Login Form
class SuperAdminLoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))


from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']



class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'address' , 'phone' ]  # Ensure profile_picture is included

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['profile_picture'].required = False  # Allow empty file



class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'  # Adjust fields as necessary
