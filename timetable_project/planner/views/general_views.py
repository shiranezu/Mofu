from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta
from ..models import (
    Timetable, TimetableEntry, Task,
    StudySession, StudyGoal, TaskBoard, StudyCategory, StudyResource,
    Note, ScheduleEntry, UserSettings
)


@login_required(login_url='planner:login')
def home(request):
    """Today's dashboard - shows all activities for today"""
    today = timezone.now()
    today_date = today.date()
    day_name = today.strftime('%A')

    # Get user's active timetables
    timetables = Timetable.objects.filter(user=request.user)

    # Today's classes from timetable
    today_classes = []
    for timetable in timetables:
        entries = TimetableEntry.objects.filter(
            timetable=timetable,
            day=day_name
        ).select_related('timeslot', 'subjectInfo').order_by('timeslot__start_time')

        for entry in entries:
            today_classes.append({
                'time': f"{entry.timeslot.start_time.strftime('%I:%M %p')} - {entry.timeslot.end_time.strftime('%I:%M %p')}",
                'subject': entry.subjectInfo.subject,
                'location': entry.subjectInfo.location,
            })

    # Today's tasks (due today or overdue)
    today_tasks = Task.objects.filter(
        task_board__user=request.user,
        due_date__lte=today_date,
        is_done=False
    ).select_related('task_board').order_by('due_date')[:10]

    # Today's study time
    today_sessions = StudySession.objects.filter(
        user=request.user,
        is_active=False,
        start_time__date=today_date
    )
    today_study_seconds = today_sessions.aggregate(
        total=Sum('duration_seconds')
    )['total'] or 0
    today_study_hours = round(today_study_seconds / 3600, 2)

    # Today's goal progress
    daily_goals = StudyGoal.objects.filter(
        user=request.user,
        goal_type='daily',
        is_active=True
    )

    goal_progress = []
    for goal in daily_goals:
        progress = goal.get_progress()
        goal_progress.append({
            'goal': goal,
            'progress': progress
        })

    # Current streak
    current_streak = StudySession.get_user_streak(request.user)

    # Active study session
    active_session = StudySession.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    # ── Onboarding checklist ──────────────────────────
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
    onboarding = None

    if not user_settings.onboarding_dismissed:
        steps = [
            {
                'label': 'Create your first timetable',
                'done': Timetable.objects.filter(user=request.user).exists(),
                'url_name': 'planner:timetable_home',
            },
            {
                'label': 'Add a task',
                'done': Task.objects.filter(task_board__user=request.user).exists(),
                'url_name': 'planner:tasks_home',
            },
            {
                'label': 'Start a study session',
                'done': StudySession.objects.filter(user=request.user).exists(),
                'url_name': 'planner:study_timer',
            },
            {
                'label': 'Create a category',
                'done': StudyCategory.objects.filter(user=request.user).exists(),
                'url_name': 'planner:manage_categories',
            },
            {
                'label': 'Write a note',
                'done': Note.objects.filter(user=request.user).exists(),
                'url_name': 'planner:notes_home',
            },
        ]
        completed_count = sum(1 for s in steps if s['done'])

        if completed_count < len(steps):
            onboarding = {
                'steps': steps,
                'completed_count': completed_count,
                'total_count': len(steps),
            }
        else:
            # All done — dismiss automatically so it never shows again
            user_settings.onboarding_dismissed = True
            user_settings.save()

    context = {
        'today_date': today_date,
        'day_name': day_name,
        'today_classes': today_classes,
        'today_tasks': today_tasks,
        'today_study_hours': today_study_hours,
        'goal_progress': goal_progress,
        'current_streak': current_streak,
        'active_session': active_session,
        'onboarding': onboarding,
    }

    return render(request, 'today.html', context)


@login_required(login_url='planner:login')
@require_POST
def dismiss_onboarding(request):
    """Permanently dismiss the onboarding checklist for this user."""
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
    user_settings.onboarding_dismissed = True
    user_settings.save()
    return JsonResponse({'status': 'ok'})
    

@login_required(login_url='planner:login')
def help(request):
    """Help page"""
    return render(request, 'help.html')


@login_required(login_url='planner:login')
def my_account(request):
    """User account page with profile info and statistics"""
    user = request.user
    
    # Account statistics
    total_sessions = StudySession.objects.filter(user=user, is_active=False).count()
    
    total_seconds = StudySession.objects.filter(
        user=user, 
        is_active=False
    ).aggregate(total=Sum('duration_seconds'))['total'] or 0
    total_hours = round(total_seconds / 3600, 2)
    
    current_streak = StudySession.get_user_streak(user)
    longest_streak = StudySession.get_longest_streak(user)
    
    # Count user's items
    timetables_count = Timetable.objects.filter(user=user).count()
    task_boards_count = TaskBoard.objects.filter(user=user).count()
    categories_count = StudyCategory.objects.filter(user=user).count()
    resources_count = StudyResource.objects.filter(user=user).count()
    notes_count = Note.objects.filter(user=user).count()
    schedule_entries_count = ScheduleEntry.objects.filter(user=user).count()
    total_study_days = StudySession.objects.filter(
        user=user, is_active=False
    ).dates('start_time', 'day').count()
    
    # Account age
    account_age = (timezone.now() - user.date_joined).days
    
    context = {
        'total_sessions': total_sessions,
        'total_hours': total_hours,
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'timetables_count': timetables_count,
        'task_boards_count': task_boards_count,
        'categories_count': categories_count,
        'resources_count': resources_count,
        'notes_count': notes_count,
        'schedule_entries_count': schedule_entries_count,
        'total_study_days': total_study_days,
        'account_age': account_age,
    }
    
    return render(request, 'account.html', context)

@login_required(login_url='planner:login')
def settings(request):
    user = request.user
    user_settings, _ = UserSettings.objects.get_or_create(user=user)
    messages_list = []

    if request.method == 'POST':
        tab = request.POST.get('tab')

        if tab == 'pomodoro':
            user_settings.pomodoro_work = max(1, int(request.POST.get('pomodoro_work', 25)))
            user_settings.pomodoro_short_break = max(1, int(request.POST.get('pomodoro_short_break', 5)))
            user_settings.pomodoro_long_break = max(1, int(request.POST.get('pomodoro_long_break', 15)))
            user_settings.pomodoro_sessions = max(1, int(request.POST.get('pomodoro_sessions', 4)))
            user_settings.save()
            messages.success(request, 'Pomodoro settings saved.')

        elif tab == 'account':
            username = request.POST.get('username', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            new_password = request.POST.get('new_password', '').strip()
            from django.contrib.auth.models import User as AuthUser
            if username and not AuthUser.objects.filter(username=username).exclude(pk=user.pk).exists():
                user.username = username
            elif username:
                messages.error(request, 'That username is already taken.')
            if first_name: user.first_name = first_name
            if last_name: user.last_name = last_name
            if email: user.email = email
            if new_password:
                user.set_password(new_password)
                user.save()
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated successfully.')
            else:
                user.save()
                messages.success(request, 'Account details saved.')

        elif tab == 'delete':
            user.delete()
            return redirect('planner:login')

        return redirect('planner:settings')

    return render(request, 'settings.html', {
        'user_settings': user_settings,
        'active_tab': request.GET.get('tab', 'appearance'),
    })