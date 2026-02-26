from .auth_views import (
    login_user, register, logout_user
)
from .timetable_views import (
    timetable_home, timetable_view, create_timetable,
    delete_timetable, add_course, add_timeslot,
    edit_entry, delete_entry, delete_timeslot,
    export_timetable_pdf
)
from .schedule_views import (
    schedule_home, schedule_view, create_schedule,
    add_schedule_item, edit_schedule_item, view_schedule_item,
    delete_schedule_item, toggle_schedule_item,
    delete_schedule, export_schedule_pdf
)
from .study_views import (
    study_timer, start_timer, stop_timer,
    update_session_notes, view_session, edit_session_notes,
    study_history, study_statistics, study_streaks,
    study_goals, add_goal, edit_goal, delete_goal, toggle_goal,
    manage_categories, add_category, delete_category,
    suggest_subjects, quick_add_category, bulk_add_categories,
    pomodoro_timer, start_pomodoro, complete_pomodoro, stop_pomodoro,
    study_resources, add_resource, edit_resource, delete_resource
)
from .general_views import home, help, my_account

from .dictionary import dictionary