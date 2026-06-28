from django.db import models
from django.contrib.auth.models import User

DAYS_OF_WEEK = [
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
]


class Subject_and_location(models.Model):
    subject = models.CharField(max_length=1000)
    location = models.CharField(max_length=100)
    category = models.ForeignKey(
        'StudyCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.subject} at {self.location}"


class Timeslot(models.Model):
    """Represents a time period in a timetable"""
    timetable = models.ForeignKey('Timetable', on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"


class Timetable(models.Model):
    DAYS_MODE_CHOICES = [
        ('weekdays', 'Mon – Fri'),
        ('full_week', 'Sun – Sat'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    days_mode = models.CharField(
        max_length=10,
        choices=DAYS_MODE_CHOICES,
        default='weekdays'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TimetableEntry(models.Model):
    """A single entry in a timetable (subject at a specific day/time)"""
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    timeslot = models.ForeignKey(Timeslot, on_delete=models.CASCADE)
    subjectInfo = models.ForeignKey(Subject_and_location, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.subjectInfo}"

    class Meta:
        unique_together = ('timetable', 'day', 'timeslot')


class TaskBoard(models.Model):
    """A user's schedule/task list"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    """A single task in a schedule"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    task_board = models.ForeignKey(TaskBoard, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    is_done = models.BooleanField(default=False)  # Keep for backward compatibility
    due_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-sync is_done with status
        if self.status == 'completed':
            self.is_done = True
        else:
            self.is_done = False
        super().save(*args, **kwargs)


class StudyCategory(models.Model):
    """Category for organizing study sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#3498db')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Study Categories"


class StudySession(models.Model):
    """A recorded study session"""
    SESSION_TAG_CHOICES = [
        ('productive', 'Productive'),
        ('struggled', 'Struggled'),
        ('review', 'Review'),
        ('learning', 'Learning New Material'),
        ('distracted', 'Distracted'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(StudyCategory, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(default=0)
    paused_seconds = models.IntegerField(default=0)  # time spent paused
    is_paused = models.BooleanField(default=False)  # currently paused
    pause_start = models.DateTimeField(null=True, blank=True)  # when pause started
    notes = models.TextField(blank=True, null=True)
    session_tag = models.CharField(max_length=20, choices=SESSION_TAG_CHOICES, blank=True, null=True)  # NEW
    productivity_rating = models.IntegerField(null=True, blank=True)  # 1-5 rating
    is_active = models.BooleanField(default=True)
    is_pomodoro = models.BooleanField(default=False)
    pomodoros_completed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_countdown = models.BooleanField(default=False)
    countdown_target_seconds = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.duration_seconds}s"

    def get_duration_display(self):
        """Convert seconds to HH:MM:SS format"""
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_actual_study_time(self):
        """Get study time minus paused time"""
        actual_seconds = self.duration_seconds - self.paused_seconds
        return max(actual_seconds, 0)

    @staticmethod
    def get_user_streak(user):
        """Calculate the user's current study streak in days"""
        from datetime import date, timedelta

        sessions = StudySession.objects.filter(
            user=user,
            is_active=False
        ).order_by('-start_time')

        if not sessions.exists():
            return 0

        study_dates = set()
        for session in sessions:
            study_dates.add(session.start_time.date())

        study_dates = sorted(study_dates, reverse=True)

        today = date.today()
        yesterday = today - timedelta(days=1)

        if today not in study_dates and yesterday not in study_dates:
            return 0

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

        study_dates = sorted(set(session.start_time.date() for session in sessions))

        if not study_dates:
            return 0

        longest_streak = 1
        current_streak = 1

        for i in range(1, len(study_dates)):
            if study_dates[i] - study_dates[i - 1] == timedelta(days=1):
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
            else:
                current_streak = 1

        return longest_streak

    class Meta:
        ordering = ['-start_time']


def format_hours_minutes(hours):
    """Convert a float hours value into a readable 'Xh Ym' / 'Ym' / 'Xh' string"""
    total_minutes = round(hours * 60)
    h, m = divmod(total_minutes, 60)
    if h > 0 and m > 0:
        return f"{h}h {m}m"
    elif h > 0:
        return f"{h}h"
    else:
        return f"{m}m"


class StudyGoal(models.Model):
    """A study goal (daily or weekly target)"""
    GOAL_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    goal_type = models.CharField(max_length=10, choices=GOAL_TYPE_CHOICES)
    target_hours = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.ForeignKey(StudyCategory, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        category_str = f" - {self.category.name}" if self.category else ""
        return f"{self.user.username} - {self.goal_type} goal: {self.target_hours}h{category_str}"
    

    def get_progress(self):
        """Calculate current progress towards this goal"""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Sum

        now = timezone.now()
        today = now.date()

        if self.goal_type == 'daily':
            sessions = StudySession.objects.filter(
                user=self.user,
                is_active=False,
                start_time__year=today.year,
                start_time__month=today.month,
                start_time__day=today.day
            )
            active_sessions = StudySession.objects.filter(
                user=self.user,
                is_active=True,
                start_time__year=today.year,
                start_time__month=today.month,
                start_time__day=today.day
            )
        else:  # weekly
            start_of_week = today - timedelta(days=today.weekday())
            sessions = StudySession.objects.filter(
                user=self.user,
                is_active=False,
                start_time__date__gte=start_of_week,
                start_time__date__lte=today
            )
            active_sessions = StudySession.objects.filter(
                user=self.user,
                is_active=True,
                start_time__date__gte=start_of_week,
                start_time__date__lte=today
            )

        if self.category:
            sessions = sessions.filter(category=self.category)
            active_sessions = active_sessions.filter(category=self.category)

        total_seconds = sessions.aggregate(total=Sum('duration_seconds'))['total'] or 0

        # Include elapsed time from any session currently in progress,
        # so goals reflect live progress instead of only updating on stop.
        for active_session in active_sessions:
            elapsed = (now - active_session.start_time).total_seconds()
            total_seconds += elapsed

        total_hours = total_seconds / 3600

        if self.target_hours > 0:
            percentage = min((total_hours / float(self.target_hours)) * 100, 100)
        else:
            percentage = 0

        return {
            'current_hours': round(total_hours, 2),
            'target_hours': float(self.target_hours),
            'percentage': int(round(percentage, 0)),
            'remaining_hours': round(max(float(self.target_hours) - total_hours, 0), 2),
            'current_display': format_hours_minutes(total_hours),
            'target_display': format_hours_minutes(float(self.target_hours)),
            'remaining_display': format_hours_minutes(max(float(self.target_hours) - total_hours, 0)),
        }

    class Meta:
        ordering = ['-created_at']

class StudyResource(models.Model):
    """A study resource link (PDF, video, article, etc.)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(StudyCategory, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    url = models.URLField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class DictionaryHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.CharField(max_length=200)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-searched_at']

    def __str__(self):
        return f"{self.user.username} — {self.word}"

class ScheduleEntry(models.Model):
    """A calendar entry for a specific date"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} — {self.date}"

    class Meta:
        ordering = ['date', 'start_time']


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='Untitled')
    category = models.ForeignKey('StudyCategory', on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-updated_at']


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    pomodoro_work = models.IntegerField(default=25)
    pomodoro_short_break = models.IntegerField(default=5)
    pomodoro_long_break = models.IntegerField(default=15)
    pomodoro_sessions = models.IntegerField(default=4)
    onboarding_dismissed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} settings"