from django.urls import path
from . import views

app_name = 'planner'

urlpatterns = [
    # ============ GENERAL ============
    path('', views.home, name='home'),
    path('help/', views.help, name='help'),

    # ============ AUTHENTICATION ============
    path('login/', views.login_user, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_user, name='logout'),

    # ============ TIMETABLES ============
    path('timetables/', views.timetable_home, name='timetable_home'),
    path('timetable/<int:timetable_id>/', views.timetable_view, name='timetable_view'),
    path('timetable/create/', views.create_timetable, name='create_timetable'),
    path('timetable/<int:timetable_id>/delete/', views.delete_timetable, name='delete_timetable'),
    path('timetable/<int:timetable_id>/export/pdf/', views.export_timetable_pdf, name='export_timetable_pdf'),
    path('add/course/', views.add_course, name='add_course'),
    path('add/timeslot/', views.add_timeslot, name='add_timeslot'),
    path('edit/<int:entry_id>/', views.edit_entry, name='edit_entry'),
    path('delete/<int:entry_id>/', views.delete_entry, name='delete_entry'),
    path('timeslot/<int:timeslot_id>/delete/', views.delete_timeslot, name='delete_timeslot'),

    # ============ SCHEDULES ============
    path('schedules/', views.schedule_home, name='schedule_home'),
    path('schedule/<int:schedule_id>/', views.schedule_view, name='schedule_view'),
    path('schedule/create/', views.create_schedule, name='create_schedule'),
    path('schedule/<int:schedule_id>/add/', views.add_schedule_item, name='add_schedule_item'),
    path('schedule/item/<int:item_id>/view/', views.view_schedule_item, name='view_schedule_item'),
    path('schedule/item/<int:item_id>/edit/', views.edit_schedule_item, name='edit_schedule_item'),
    path('schedule/item/<int:item_id>/delete/', views.delete_schedule_item, name='delete_schedule_item'),
    path('schedule/item/<int:item_id>/toggle/', views.toggle_schedule_item, name='toggle_schedule_item'),
    path('schedule/<int:schedule_id>/delete/', views.delete_schedule, name='delete_schedule'),
    path('schedule/<int:schedule_id>/export/pdf/', views.export_schedule_pdf, name='export_schedule_pdf'),

    # ============ STUDY TIMER ============
    path('study/timer/', views.study_timer, name='study_timer'),
    path('study/start/', views.start_timer, name='start_timer'),
    path('study/stop/<int:session_id>/', views.stop_timer, name='stop_timer'),
    path('study/session/<int:session_id>/', views.view_session, name='view_session'),
    path('study/session/<int:session_id>/notes/', views.update_session_notes, name='update_session_notes'),
    path('study/session/<int:session_id>/edit-notes/', views.edit_session_notes, name='edit_session_notes'),
    path('study/history/', views.study_history, name='study_history'),
    path('study/statistics/', views.study_statistics, name='study_statistics'),
    path('study/streaks/', views.study_streaks, name='study_streaks'),

    # ============ STUDY GOALS ============
    path('study/goals/', views.study_goals, name='study_goals'),
    path('study/goals/add/', views.add_goal, name='add_goal'),
    path('study/goals/<int:goal_id>/edit/', views.edit_goal, name='edit_goal'),
    path('study/goals/<int:goal_id>/delete/', views.delete_goal, name='delete_goal'),
    path('study/goals/<int:goal_id>/toggle/', views.toggle_goal, name='toggle_goal'),

    # ============ STUDY CATEGORIES ============
    path('study/categories/', views.manage_categories, name='manage_categories'),
    path('study/categories/add/', views.add_category, name='add_category'),
    path('study/categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('study/subjects/suggest/', views.suggest_subjects, name='suggest_subjects'),
    path('study/subjects/quick-add/<str:subject_name>/', views.quick_add_category, name='quick_add_category'),
    path('study/subjects/bulk-add/', views.bulk_add_categories, name='bulk_add_categories'),

    # ============ STUDY RESOURCES ============
    path('study/resources/', views.study_resources, name='study_resources'),
    path('study/resources/add/', views.add_resource, name='add_resource'),
    path('study/resources/<int:resource_id>/edit/', views.edit_resource, name='edit_resource'),
    path('study/resources/<int:resource_id>/delete/', views.delete_resource, name='delete_resource'),

    # ============ POMODORO TIMER ============
    path('study/pomodoro/', views.pomodoro_timer, name='pomodoro_timer'),
    path('study/pomodoro/start/', views.start_pomodoro, name='start_pomodoro'),
    path('study/pomodoro/<int:session_id>/complete/', views.complete_pomodoro, name='complete_pomodoro'),
    path('study/pomodoro/<int:session_id>/stop/', views.stop_pomodoro, name='stop_pomodoro'),
]