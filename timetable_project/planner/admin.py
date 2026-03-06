from django.contrib import admin
from .models import (
    Subject_and_location, Timeslot, TimetableEntry, Timetable,
    Schedule, ScheduleItem, StudyCategory, StudySession,
    StudyGoal, StudyResource
)

admin.site.register(Subject_and_location)
admin.site.register(Timeslot)
admin.site.register(TimetableEntry)
admin.site.register(Timetable)
admin.site.register(Schedule)
admin.site.register(ScheduleItem)
admin.site.register(StudyCategory)
admin.site.register(StudySession)
admin.site.register(StudyGoal)
admin.site.register(StudyResource)


class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'start_time', 'duration_seconds', 'is_active')
    list_filter = ('user', 'is_active', 'category')
    search_fields = ('user__username', 'notes')