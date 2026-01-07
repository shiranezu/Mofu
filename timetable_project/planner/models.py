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
    start_time=models.TimeField()
    end_time=models.TimeField()

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
