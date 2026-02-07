from django.forms import ModelForm, ClearableFileInput
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import *

from datetime import datetime
from django.utils import timezone

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        
        try:
            validate_password(password1, self.instance)
        except ValidationError as error:
            print(error.messages)
            raise forms.ValidationError(error.messages)

        if not username or not email or not password1 or not password2:
            raise forms.ValidationError('All fields must be filled out.')

class NoticeForm(ModelForm):
    class Meta:
        model = Notice
        # ADDED: 'description' to fields
        fields = ['heading', 'description', 'notice_img', 'removal_date']
        widgets = {
            'removal_date': forms.DateInput(attrs={'type': 'date'}),
            'notice_img': ClearableFileInput(attrs={'accept': 'image/png, image/jpeg, application/pdf'}),
            # ADDED: Textarea widget for description
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter description (0-70 words)...'}),
        }
        help_texts = {
            'notice_img': 'Upload Notice (Max size: 5MB)',
        }

    def clean_notice_img(self):
        notice_img = self.cleaned_data.get('notice_img')
        if notice_img:
            content_type = notice_img.content_type
            if content_type == 'application/pdf':
                return notice_img
            elif content_type in ['image/png', 'image/jpeg']:
                return notice_img
            else:
                raise forms.ValidationError('Unsupported file type. Please upload PNG, JPEG, or PDF files.')

    def clean(self):
        cleaned_data = super().clean()
        removal_date = cleaned_data.get('removal_date')
        current_date = timezone.now().date()
        if removal_date < current_date:
            raise forms.ValidationError("Removal date must be today or in the future.")

class CompetitionForm(ModelForm):
    class Meta:
        model = Competition
        fields = ['department', 'name', 'description', 'date', 'link', 'poster']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            # ADDED: Textarea widget for description
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter description (0-70 words)...'}),
        }
        help_texts = {
            'department': 'Only enter the dept if your username is not your dept name',
            'poster': 'Upload Poster (Max size: 5MB)',
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        description = cleaned_data.get('description')
        date = cleaned_data.get('date')
        link = cleaned_data.get('link')
        poster = cleaned_data.get('poster')

        if not name or not description or not link or not poster:
            raise forms.ValidationError('All fields must be filled out.')
        
        current_date = timezone.now().date()
        if date <= current_date:
            raise forms.ValidationError("The date must be in the future.")

class SurveyForm(ModelForm):
    class Meta:
        model = Survey
        fields = ['department', 'name', 'description', 'link']
        # ADDED: Textarea widget for description
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter description (0-70 words)...'}),
        }
        help_texts = {
            'department': 'Only enter the dept if your username is not your dept name',
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        description = cleaned_data.get('description')
        link = cleaned_data.get('link')

        if not name or not description or not link:
            raise forms.ValidationError('All fields must be filled out.')

class FestForm(ModelForm):
    class Meta:
        model = Fest
        fields = ['department', 'name', 'description', 'date', 'poster']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            # ADDED: Textarea widget for description
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter description (0-70 words)...'}),
        }
        help_texts = {
            'department': 'Only enter the dept if your username is not your dept name',
            'poster': 'Upload Poster (Max size: 5MB)',
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        description = cleaned_data.get('description')
        date = cleaned_data.get('date')
        poster = cleaned_data.get('poster')

        if not name or not description or not date or not poster:
            raise forms.ValidationError('All fields must be filled out.')
        
        current_date = timezone.now().date()
        if date <= current_date:
            raise forms.ValidationError("The date must be in the future.")


class SeminarForm(ModelForm):
    # 1. Remove 'allow_empty=True', just keep required=False
    link = forms.URLField(required=False)

    class Meta:
        model = Seminar
        # ADDED: 'description' to fields
        fields = ['department', 'name', 'description', 'date', 'link', 'poster']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            # ADDED: Textarea widget for description
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter description (0-70 words)...'}),
        }
        help_texts = {
            'department': 'Only enter the dept if your username is not your dept name',
            'poster': 'Upload Poster (Max size: 5MB)',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        description = cleaned_data.get('description') # Get description
        date = cleaned_data.get('date')
        poster = cleaned_data.get('poster')

        # 2. Link is not checked here, so it can be empty. Description checked here (optional, model validator handles strictness)
        if not name or not date or not poster:
            raise forms.ValidationError('Please fill in Name, Date, and Poster.')
        
        current_date = timezone.now().date()
        if date < current_date:
            raise forms.ValidationError("The date must be in the future.")

class StudentInitiativeForm(ModelForm):
    class Meta:
        model = StudentInitiative
        fields = ['name', 'student_name', 'description']
        # ADDED: Textarea widget for description
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter description (0-70 words)...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        student_name = cleaned_data.get('student_name')
        description = cleaned_data.get('description')

        if not name or not student_name or not description:
            raise forms.ValidationError('All fields must be filled out.')

class AlumniForm(ModelForm):
    class Meta:
        model = Alumni
        fields = ['department', 'name', 'batch', 'information', 'linkedin_link', 'picture']
        # ADDED: Textarea widget for information (Alumni uses 'information' instead of 'description')
        widgets = {
            'information': forms.Textarea(attrs={'rows': 4}),
        }
        help_texts = {
            'batch': 'Enter full year. Example: 2020',
            'department': 'Only enter the dept if your username is not your dept name',
            'picture': 'Upload Poster (Max size: 5MB)',
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        batch = cleaned_data.get('batch')
        information = cleaned_data.get('information')
        picture = cleaned_data.get('picture')

        current_year = timezone.now().year
        try:
            batch_year = int(batch)
        except ValueError:
            raise forms.ValidationError('Batch year must be a valid integer.')

        if not (current_year - 50 < batch_year <= current_year):
            raise forms.ValidationError('Batch refers to the year of passing from college of a student. Enter a valid batch.')

        if not name or not batch or not information or not picture:
            raise forms.ValidationError('All fields must be filled out.')