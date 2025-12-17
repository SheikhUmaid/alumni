from django import forms
import uuid
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile, Job, Mentorship, Event, Application, Notification

class CustomUserCreationForm(UserCreationForm):
    branch = forms.ChoiceField(choices=Profile.BRANCH_CHOICES, required=False, label="Branch (for students)")
    graduation_year = forms.IntegerField(required=False, label="Graduation Year (for alumni)")
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        if not user.username:
            user.username = str(uuid.uuid4())
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['department', 'branch', 'graduation_year', 'skills', 'resume', 'company', 'designation', 'linkedin_url']

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'company', 'branch', 'job_type', 'location']

class MentorshipForm(forms.ModelForm):
    class Meta:
        model = Mentorship
        fields = ['expertise_areas', 'availability', 'max_mentees']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date_time', 'mode', 'registration_limit']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [] # Status is updated by admin/alumni, students just click apply
