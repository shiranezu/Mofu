from django.urls import path
from . import views

app_name = 'planner'

urlpatterns = [
    path('', views.select_timetable, name='home'),
    path('timetable/<int:timetable_id>/', views.timetable_view, name='timetable_view'),
    path('timetable/create/', views.create_timetable, name='create_timetable'),
    path('add/course/', views.add_course, name='add_course'),
    path('add/timeslot/', views.add_timeslot, name='add_timeslot'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('edit/', views.edit_view, name='edit'),
    path('edit/<int:entry_id>/', views.edit_entry, name='edit_entry'),
    path('delete/<int:entry_id>/', views.delete_entry, name='delete_entry'),
    path('timetable/<int:timetable_id>/delete/', views.delete_timetable, name='delete_timetable'),
    path('timeslot/<int:timeslot_id>/delete/', views.delete_timeslot, name='delete_timeslot'),
    path('timetable/<int:timetable_id>/export/pdf/', views.export_timetable_pdf, name='export_timetable_pdf'),

    # Schedule management
    path('schedules/', views.select_schedule, name='select_schedule'),
    path('schedule/<int:schedule_id>/', views.schedule_view, name='schedule_view'),
    path('schedule/create/', views.create_schedule, name='create_schedule'),
    path('schedule/<int:schedule_id>/add/', views.add_schedule_item, name='add_schedule_item'),
    path('schedule/item/<int:item_id>/edit/', views.edit_schedule_item, name='edit_schedule_item'),
    path('schedule/item/<int:item_id>/delete/', views.delete_schedule_item, name='delete_schedule_item'),
    path('schedule/<int:schedule_id>/delete/', views.delete_schedule, name='delete_schedule'),
    path('schedule/<int:schedule_id>/export/pdf/', views.export_schedule_pdf, name='export_schedule_pdf'),
    # Other Pages
    path('help/', views.help, name='help'),


]