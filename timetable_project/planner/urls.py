from django.urls import path
from . import views

app_name = 'planner'

urlpatterns = [
    # GENERAL
    path('', views.home, name='home'),
    path('help/', views.help, name='help'),
    path('account/', views.my_account, name='my_account'),

    # AUTHENTICATION
    path('login/', views.login_user, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_user, name='logout'),

    # TIMETABLES
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
    path('timetable/<int:timetable_id>/toggle-days/', views.toggle_days_mode, name='toggle_days_mode'),

    # TASKS
    path('tasks/', views.tasks_home, name='tasks_home'),
    path('tasks/<int:board_id>/', views.task_board, name='task_board'),
    path('tasks/create/', views.create_task_board, name='create_task_board'),
    path('tasks/<int:board_id>/add/', views.add_task, name='add_task'),
    path('tasks/item/<int:task_id>/view/', views.view_task, name='view_task'),
    path('tasks/item/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('tasks/item/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('tasks/item/<int:task_id>/toggle/', views.toggle_task, name='toggle_task'),
    path('tasks/<int:board_id>/delete/', views.delete_task_board, name='delete_task_board'),
    path('tasks/<int:board_id>/export/pdf/', views.export_tasks_pdf, name='export_tasks_pdf'),

    # focus
    path('study/timer/', views.study_timer, name='study_timer'),
    path('study/start/', views.start_timer, name='start_timer'),
    path('study/stop/<int:session_id>/', views.stop_timer, name='stop_timer'),
    path('study/session/<int:session_id>/', views.view_session, name='view_session'),
    path('study/session/<int:session_id>/notes/', views.update_session_notes, name='update_session_notes'),
    path('study/session/<int:session_id>/edit-notes/', views.edit_session_notes, name='edit_session_notes'),
    path('study/history/', views.study_history, name='study_history'),
    path('study/statistics/', views.study_statistics, name='study_statistics'),
    path('study/streaks/', views.study_streaks, name='study_streaks'),
    path('study/pause/<int:session_id>/', views.pause_timer, name='pause_timer'),
    path('study/resume/<int:session_id>/', views.resume_timer, name='resume_timer'),
    path('study/stop-summary/<int:session_id>/', views.stop_timer_with_summary, name='stop_timer_with_summary'),
    path('study/session/<int:session_id>/delete/', views.delete_session, name='delete_session'),
    path('study/history/clear/', views.clear_all_history, name='clear_all_history'),

    # GOALS
    path('study/goals/', views.study_goals, name='study_goals'),
    path('study/goals/add/', views.add_goal, name='add_goal'),
    path('study/goals/<int:goal_id>/edit/', views.edit_goal, name='edit_goal'),
    path('study/goals/<int:goal_id>/delete/', views.delete_goal, name='delete_goal'),
    path('study/goals/<int:goal_id>/toggle/', views.toggle_goal, name='toggle_goal'),

    # CATEGORIES
    path('study/categories/', views.manage_categories, name='manage_categories'),
    path('study/categories/add/', views.add_category, name='add_category'),
    path('study/categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('study/subjects/suggest/', views.suggest_subjects, name='suggest_subjects'),
    path('study/subjects/quick-add/<str:subject_name>/', views.quick_add_category, name='quick_add_category'),
    path('study/subjects/bulk-add/', views.bulk_add_categories, name='bulk_add_categories'),

    # RESOURCES
    path('study/resources/', views.study_resources, name='study_resources'),
    path('study/resources/add/', views.add_resource, name='add_resource'),
    path('study/resources/<int:resource_id>/edit/', views.edit_resource, name='edit_resource'),
    path('study/resources/<int:resource_id>/delete/', views.delete_resource, name='delete_resource'),

    # POMODORO TIMER 
    path('study/pomodoro/', views.pomodoro_timer, name='pomodoro_timer'),
    path('study/pomodoro/start/', views.start_pomodoro, name='start_pomodoro'),
    path('study/pomodoro/<int:session_id>/complete/', views.complete_pomodoro, name='complete_pomodoro'),
    path('study/pomodoro/<int:session_id>/stop/', views.stop_pomodoro, name='stop_pomodoro'),
    path('study/pomodoro/<int:session_id>/pause/', views.pause_pomodoro, name='pause_pomodoro'),
    path('study/pomodoro/<int:session_id>/resume/', views.resume_pomodoro, name='resume_pomodoro'),

    # COUNTDOWN TIMER
    path('study/countdown/start/', views.start_countdown, name='start_countdown'),
path('study/countdown/<int:session_id>/stop/', views.stop_countdown, name='stop_countdown'),
path('study/countdown/<int:session_id>/complete/', views.complete_countdown, name='complete_countdown'),

    # DICTIONARY
    path('study/dictionary/', views.dictionary, name='dictionary'),
    path('study/dictionary/clear/', views.clear_dictionary_history, name='clear_dictionary_history'),

    # QUICK ADD
    path('tasks/quick-add/', views.quick_add_task, name='quick_add_task'),

    # SCHEDULE (Dynamic Calendar)
    path('schedule/', views.schedule_home, name='schedule_home'),
    path('schedule/add/', views.add_schedule_entry, name='add_schedule_entry'),
    path('schedule/<int:entry_id>/', views.view_schedule_entry, name='view_schedule_entry'),
    path('schedule/<int:entry_id>/edit/', views.edit_schedule_entry, name='edit_schedule_entry'),
    path('schedule/<int:entry_id>/delete/', views.delete_schedule_entry, name='delete_schedule_entry'),
    path('schedule/<int:entry_id>/toggle/', views.toggle_schedule_entry, name='toggle_schedule_entry'),

    # NOTES
    path('notes/', views.notes_home, name='notes_home'),
    path('notes/create/', views.create_note, name='create_note'),
    path('notes/<int:note_id>/', views.note_detail, name='note_detail'),
    path('notes/<int:note_id>/delete/', views.delete_note, name='delete_note'),
    path('notes/<int:note_id>/save/', views.save_note, name='save_note'),

    # SETTINGS
    path('settings/', views.settings, name='settings'),
]