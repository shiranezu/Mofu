from .auth_views import (
    login_user, register, logout_user
)
from .timetable_views import (
    timetable_home, timetable_view, create_timetable,
    delete_timetable, add_course, add_timeslot,
    edit_entry, delete_entry, delete_timeslot,
    export_timetable_pdf, toggle_days_mode,
)
from .task_views import (
    tasks_home, task_board, create_task_board,
    add_task, edit_task, view_task,
    delete_task, toggle_task,
    delete_task_board, export_tasks_pdf, quick_add_task
)
from .study_views import (
    study_timer, start_timer, stop_timer,
    pause_timer, resume_timer, stop_timer_with_summary,
    update_session_notes, view_session, edit_session_notes,
    study_history, study_statistics, study_streaks,
    study_goals, add_goal, edit_goal, delete_goal, toggle_goal,
    manage_categories, add_category, delete_category,
    suggest_subjects, quick_add_category, bulk_add_categories,
    pomodoro_timer, start_pomodoro, pause_pomodoro, resume_pomodoro, complete_pomodoro, stop_pomodoro,
    study_resources, add_resource, edit_resource, delete_resource, start_countdown, stop_countdown,
    complete_countdown, delete_session, clear_all_history,
)
from .general_views import home, help, my_account, settings, dismiss_onboarding
from .dictionary import dictionary, clear_dictionary_history
from .schedule_views import (
    schedule_home, add_schedule_entry, view_schedule_entry,
    edit_schedule_entry, delete_schedule_entry, toggle_schedule_entry,
)
from .note_views import (
    notes_home, create_note, note_detail, delete_note, save_note
)
from .export_views import export_data
from .import_views import import_data