from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta
from ..models import (
    Timetable, TimetableEntry, Task, 
    StudySession, StudyGoal, TaskBoard, StudyCategory, StudyResource
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
    
    context = {
        'today_date': today_date,
        'day_name': day_name,
        'today_classes': today_classes,
        'today_tasks': today_tasks,
        'today_study_hours': today_study_hours,
        'goal_progress': goal_progress,
        'current_streak': current_streak,
        'active_session': active_session,
    }
    
    return render(request, 'today.html', context)


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
        'account_age': account_age,
    }
    
    return render(request, 'account.html', context)