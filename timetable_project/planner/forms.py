from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    ScheduleEntry,
    Subject_and_location, Timeslot, Task, TaskBoard,
    StudyCategory, StudyGoal, StudyResource, DAYS_OF_WEEK, Timetable
)


class Subject_and_locationForm(forms.ModelForm):
    day = forms.ChoiceField(choices=DAYS_OF_WEEK)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        timetable = kwargs.pop('timetable', None)
        super().__init__(*args, **kwargs)
        if timetable:
            self.fields['timeslot'] = forms.ModelChoiceField(
                queryset=Timeslot.objects.filter(timetable=timetable)
            )
        if user:
            self.fields['category'].queryset = StudyCategory.objects.filter(user=user)
            self.fields['category'].required = False
            self.fields['category'].empty_label = "No Category"

    class Meta:
        model = Subject_and_location
        fields = ['subject', 'location', 'category']

class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['name']

class TimeslotForm(forms.ModelForm):
    """Form for creating timeslots"""
    class Meta:
        model = Timeslot
        fields = ['start_time', 'end_time']


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
    class Meta:
        model = StudyGoal
        fields = ['name', 'goal_type', 'target_hours', 'category']
        widgets = {
            'target_hours': forms.NumberInput(attrs={'step': '0.5', 'min': '0.5'})
        }
        labels = {
            'goal_type': 'Goal Type',
            'target_hours': 'Target Hours',
            'category': 'Category (Optional - leave blank for all categories)'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = StudyCategory.objects.filter(user=user)
            self.fields['category'].required = False
            self.fields['category'].empty_label = "All Categories"


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