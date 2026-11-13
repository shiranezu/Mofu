from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from datetime import time
from .models import (
    ScheduleEntry,
    Subject_and_location, Timeslot, Task, TaskBoard,
    StudyCategory, StudyGoal, StudyResource, DAYS_OF_WEEK, Timetable
)


class Subject_and_locationForm(forms.ModelForm):
    class Meta:
        model = Subject_and_location
        fields = ['subject', 'location', 'category']
        labels = {'location': 'Extra info'}
        widgets = {
            'location': forms.TextInput(attrs={'placeholder': 'Room, lecturer, notes...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['location'].required = False
        if user:
            self.fields['category'].queryset = StudyCategory.objects.filter(user=user)
        self.fields['category'].required = False
        self.fields['category'].empty_label = "No Category"
        

class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['name']

class TimeslotForm(forms.ModelForm):
    """Form for creating timeslots"""
    class Meta:
        model = Timeslot
        fields = ['start_time', 'end_time']



PRESET_MINUTES = {'hourly': 60, 'bihourly': 120}

class TimeslotPresetForm(forms.Form):
    """Generates a run of timeslots between two times"""
    preset = forms.ChoiceField(
        choices=[('hourly', 'Hourly'), ('bihourly', 'Every 2 hours')],
        initial='hourly',
    )
    start_time = forms.TimeField(
        initial=time(8, 0),
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
    )
    end_time = forms.TimeField(
        initial=time(17, 0),
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
    )

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_time')
        end = cleaned.get('end_time')
        preset = cleaned.get('preset')

        if start and end and preset:
            span = (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)
            if span <= 0:
                raise forms.ValidationError("End time must be after the start time.")
            step = PRESET_MINUTES[preset]
            if span < step:
                raise forms.ValidationError(
                    f"The range must be at least {step // 60} hour{'s' if step > 60 else ''} long."
                )
        return cleaned


class RegistrationForm(UserCreationForm):
    """User registration form"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']


class TaskBoardForm(forms.ModelForm):
    """Form for creating schedules"""
    class Meta:
        model = TaskBoard
        fields = ["name"]


class TaskForm(forms.ModelForm):
    """Form for creating schedule items/tasks"""
    class Meta:
        model = Task
        fields = ["title", "description", "priority", "status", "due_date"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"})
        }

class StudyCategoryForm(forms.ModelForm):
    """Form for creating study categories"""
    class Meta:
        model = StudyCategory
        fields = ['name', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'})
        }


class StudyGoalForm(forms.ModelForm):
    """Form for creating study goals"""

    target_hours_input = forms.IntegerField(
        label='Hours',
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={'min': '0', 'placeholder': '0'})
    )
    target_minutes_input = forms.IntegerField(
        label='Minutes',
        min_value=0,
        max_value=59,
        initial=0,
        widget=forms.NumberInput(attrs={'min': '0', 'max': '59', 'placeholder': '0'})
    )

    class Meta:
        model = StudyGoal
        fields = ['name', 'goal_type', 'category']
        labels = {
            'goal_type': 'Goal Type',
            'category': 'Category (Optional - leave blank for all categories)'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = StudyCategory.objects.filter(user=user)
            self.fields['category'].required = False
            self.fields['category'].empty_label = "All Categories"

        # Pre-fill hours/minutes when editing an existing goal
        if self.instance and self.instance.pk and self.instance.target_hours:
            total_minutes = round(float(self.instance.target_hours) * 60)
            h, m = divmod(total_minutes, 60)
            self.fields['target_hours_input'].initial = h
            self.fields['target_minutes_input'].initial = m

    def clean(self):
        cleaned_data = super().clean()
        hours = cleaned_data.get('target_hours_input') or 0
        minutes = cleaned_data.get('target_minutes_input') or 0

        if hours == 0 and minutes == 0:
            raise forms.ValidationError("Target must be greater than 0.")

        cleaned_data['target_hours'] = hours + (minutes / 60)
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.target_hours = self.cleaned_data['target_hours']
        if commit:
            instance.save()
        return instance


class StudyResourceForm(forms.ModelForm):
    """Form for adding study resource links"""
    class Meta:
        model = StudyResource
        fields = ['title', 'url', 'category', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = StudyCategory.objects.filter(user=user)
            self.fields['category'].required = False

class ScheduleEntryForm(forms.ModelForm):
    class Meta:
        model = ScheduleEntry
        fields = ['title', 'date', 'start_time', 'end_time', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), required=True)