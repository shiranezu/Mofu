from django import forms
from .models import StudyGoal, Subject_and_location, Timeslot, DAYS_OF_WEEK, ScheduleItem, Schedule, StudyCategory, StudySession 
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Timetable forms
class Subject_and_locationForm(forms.ModelForm):
    day = forms.ChoiceField(choices=DAYS_OF_WEEK)
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['timeslot'] = forms.ModelChoiceField(
                queryset=Timeslot.objects.filter(user=user)
            )
    
    class Meta:
        model = Subject_and_location
        fields = ['subject', 'location']

class TimeslotForm(forms.ModelForm):
    class Meta:
        model = Timeslot
        fields = ['start_time', 'end_time']

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']



# Schedule Forms
class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ["name"]


class ScheduleItemForm(forms.ModelForm):
    class Meta:
        model = ScheduleItem
        fields = ["title", "description", "due_date", "is_done"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"})
        }

# study sessions

class StudyCategoryForm(forms.ModelForm):
    class Meta:
        model = StudyCategory
        fields = ['name', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'})
        }


class StudySessionForm(forms.ModelForm):
    class Meta:
        model = StudySession
        fields = ['category', 'notes']

class StudyGoalForm(forms.ModelForm):
    class Meta:
        model = StudyGoal
        fields = ['goal_type', 'target_hours', 'category']
        widgets = {
            'target_hours': forms.NumberInput(attrs={'step': '0.5', 'min': '0.5'})
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = StudyCategory.objects.filter(user=user)
            self.fields['category'].required = False