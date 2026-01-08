from django.contrib import admin
from .models import Subject_and_location, Timeslot, TimetableEntry, Timetable, Schedule, ScheduleItem, StudyCategory, StudySession
from .forms import Subject_and_locationForm, TimeslotForm, RegistrationForm, ScheduleForm, ScheduleItemForm

admin.site.register(Subject_and_location)
admin.site.register(Timeslot)
admin.site.register(TimetableEntry)
admin.site.register(Timetable)
admin.site.register(Schedule)
admin.site.register(ScheduleItem)
admin.site.register(StudyCategory)
admin.site.register(StudySession)
# Register your models here.

