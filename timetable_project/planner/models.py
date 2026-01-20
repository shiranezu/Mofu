from django.db import models
from django.contrib.auth.models import User

DAYS_OF_WEEK=[
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
]

class Subject_and_location(models.Model):
    subject=models.CharField(max_length=1000)
    location=models.CharField(max_length=100)

    def __str__(self):
        return f"{self.subject} at {self.location}"


class Timeslot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Remove null=True, blank=True
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"


# Experimental
class Timetable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name   

class TimetableEntry(models.Model):
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    user=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    day=models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    timeslot=models.ForeignKey(Timeslot, on_delete=models.CASCADE)
    subjectInfo=models.ForeignKey(Subject_and_location, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.subjectInfo}"

    class Meta:
        unique_together=('timetable','day','timeslot') 


# Scheduled Task Model
class Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class ScheduleItem(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    is_done = models.BooleanField(default=False)
    due_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title
    

# study sessions

class StudyCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#3498db')  # Hex color code
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Study Categories"


class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(StudyCategory, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(default=0)  # Total seconds studied
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)  # True if timer is running
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.duration_seconds}s"
    
    def get_duration_display(self):
        """Convert seconds to HH:MM:SS format"""
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    @staticmethod
    def get_user_streak(user):
        """Calculate the user's current study streak"""
        from datetime import date, timedelta
        
        # Get all completed sessions for this user, ordered by date
        sessions = StudySession.objects.filter(
            user=user, 
            is_active=False
        ).order_by('-start_time')
        
        if not sessions.exists():
            return 0
        
        # Get unique dates that have study sessions
        study_dates = set()
        for session in sessions:
            study_dates.add(session.start_time.date())
        
        # Sort dates in descending order
        study_dates = sorted(study_dates, reverse=True)
        
        # Check if user studied today or yesterday (to keep streak alive)
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        if today not in study_dates and yesterday not in study_dates:
            return 0  # Streak broken
        
        # Count consecutive days
        streak = 0
        current_date = today if today in study_dates else yesterday
        
        while current_date in study_dates:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak
    
    @staticmethod
    def get_longest_streak(user):
        """Calculate the user's longest streak ever"""
        from datetime import timedelta
        
        sessions = StudySession.objects.filter(
            user=user,
            is_active=False
        ).order_by('start_time')
        
        if not sessions.exists():
            return 0
        
        # Get unique dates
        study_dates = sorted(set(session.start_time.date() for session in sessions))
        
        if not study_dates:
            return 0
        
        longest_streak = 1
        current_streak = 1
        
        for i in range(1, len(study_dates)):
            if study_dates[i] - study_dates[i-1] == timedelta(days=1):
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1
        
        return longest_streak
    
    class Meta:
        ordering = ['-start_time']





















    class Meta:
        ordering = ['-start_time']
