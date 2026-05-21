from django.contrib import admin
from .models import (
    ScheduleEntry,
    Subject_and_location, Timeslot, TimetableEntry, Timetable,
    TaskBoard, Task, StudyCategory, StudySession,
    StudyGoal, StudyResource, DictionaryHistory
)

admin.site.register(Subject_and_location)
admin.site.register(Timeslot)
admin.site.register(TimetableEntry)
admin.site.register(Timetable)
admin.site.register(TaskBoard)
admin.site.register(Task)
admin.site.register(StudyCategory)
admin.site.register(StudySession)
admin.site.register(StudyGoal)
admin.site.register(StudyResource)
admin.site.register(DictionaryHistory)
admin.site.register(ScheduleEntry)

class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'start_time', 'duration_seconds', 'is_active')
    list_filter = ('user', 'is_active', 'category')
    search_fields = ('user__username', 'notes')
    