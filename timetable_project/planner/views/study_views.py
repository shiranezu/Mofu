from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta
import json
from ..models import StudySession, StudyCategory, StudyGoal, Timetable, TimetableEntry, StudyResource
from ..forms import StudyResourceForm



@login_required(login_url='planner:login')
def study_timer(request):
    """Main timer page"""
    from django.db.models import Sum
    categories = StudyCategory.objects.filter(user=request.user)
    today = timezone.now().date()

    active_session  = StudySession.objects.filter(
        user=request.user, is_active=True,
        is_pomodoro=False, is_countdown=False
    ).first()
    active_pomodoro = StudySession.objects.filter(
        user=request.user, is_active=True, is_pomodoro=True
    ).first()
    active_countdown = StudySession.objects.filter(
        user=request.user, is_active=True, is_countdown=True
    ).first()

    today_seconds = StudySession.objects.filter(
        user=request.user, is_active=False,
        start_time__date=today
    ).aggregate(total=Sum('duration_seconds'))['total'] or 0

    today_sessions_count = StudySession.objects.filter(
        user=request.user, is_active=False,
        start_time__date=today
    ).count()

    return render(request, 'study/timer.html', {
        'categories': categories,
        'active_session': active_session,
        'active_pomodoro': active_pomodoro,
        'active_countdown': active_countdown,
        'today_study_hours': round(today_seconds / 3600, 2),
        'today_sessions_count': today_sessions_count,
        'current_streak': StudySession.get_user_streak(request.user),
    })


@login_required(login_url='planner:login')
def start_timer(request):
    """Start a new study session"""
    if request.method == 'POST':
        category_id = request.POST.get('category')
        category = None
        if category_id:
            category = StudyCategory.objects.get(id=category_id, user=request.user)

        active_session = StudySession.objects.filter(user=request.user, is_active=True).first()
        if active_session:
            messages.warning(request, "You already have an active session!")
            return redirect('planner:study_timer')

        StudySession.objects.create(
            user=request.user,
            category=category,
            start_time=timezone.now(),
            is_active=True
        )
        messages.success(request, "Study session started!")
    return redirect('planner:study_timer')


@login_required(login_url='planner:login')
def pause_timer(request, session_id):
    """Pause an active study session"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user, is_active=True)
    
    if not session.is_paused:
        session.is_paused = True
        session.pause_start = timezone.now()
        session.save()
        messages.success(request, "Timer paused")
    
    return redirect('planner:study_timer')


@login_required(login_url='planner:login')
def resume_timer(request, session_id):
    """Resume a paused study session"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user, is_active=True)
    
    if session.is_paused and session.pause_start:
        
        pause_duration = int((timezone.now() - session.pause_start).total_seconds())
        session.paused_seconds += pause_duration
        session.is_paused = False
        session.pause_start = None
        session.save()
        messages.success(request, "Timer resumed")
    
    return redirect('planner:study_timer')


@login_required(login_url='planner:login')
def stop_timer_with_summary(request, session_id):
    """Stop timer with optional summary/feedback"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user, is_active=True)
    
    if request.method == 'POST':
        # feedback form
        session_tag = request.POST.get('session_tag')
        productivity_rating = request.POST.get('productivity_rating')
        notes = request.POST.get('notes', '')
        
        # Stop the session
        session.end_time = timezone.now()
        
        # Calculate total elapsed time
        elapsed = int((session.end_time - session.start_time).total_seconds())
        
        # If currently paused, add current pause time
        if session.is_paused and session.pause_start:
            pause_duration = int((timezone.now() - session.pause_start).total_seconds())
            session.paused_seconds += pause_duration
        
        session.duration_seconds = elapsed - session.paused_seconds  # Actual study time
        session.session_tag = session_tag if session_tag else None
        session.productivity_rating = int(productivity_rating) if productivity_rating else None
        session.notes = notes
        session.is_active = False
        session.is_paused = False
        session.save()
        
        messages.success(request, f"Session completed! Duration: {session.get_duration_display()}")
        return redirect('planner:study_timer')
    
    return render(request, 'study/stop_session_summary.html', {'session': session})


@login_required(login_url='planner:login')
def stop_timer(request, session_id):
    """Stop a study session"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user, is_active=True)
    session.end_time = timezone.now()
    elapsed = int((session.end_time - session.start_time).total_seconds())
    if session.is_paused and session.pause_start:
        pause_duration = int((timezone.now() - session.pause_start).total_seconds())
        session.paused_seconds += pause_duration
    session.duration_seconds = elapsed - session.paused_seconds
    session.is_active = False
    session.is_paused = False
    session.save()
    messages.success(request, f"Session completed! Duration: {session.get_duration_display()}")
    return redirect('planner:study_timer')


@login_required(login_url='planner:login')
def update_session_notes(request, session_id):
    """Update notes for an active study session"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user)
    if request.method == 'POST':
        session.notes = request.POST.get('notes', '')
        session.save()
        messages.success(request, "Notes saved!")
    if session.is_pomodoro:
        return redirect('planner:pomodoro_timer')
    return redirect('planner:study_timer')

@login_required(login_url='planner:login')
def view_session(request, session_id):
    """View details of a study session"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user)
    return render(request, 'study/session_detail.html', {'session': session})


@login_required(login_url='planner:login')
def edit_session_notes(request, session_id):
    """Edit notes for a completed session"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user)
    if request.method == 'POST':
        session.notes = request.POST.get('notes', '')
        session.save()
        messages.success(request, "Notes updated!")
        return redirect('planner:study_history')
    return render(request, 'study/edit_session_notes.html', {'session': session})


@login_required(login_url='planner:login')
def study_history(request):
    """View all past study sessions"""
    from django.core.paginator import Paginator

    sessions = StudySession.objects.filter(user=request.user, is_active=False)
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # Filters
    category_id = request.GET.get('category', '')
    session_type = request.GET.get('type', '')
    sort_by = request.GET.get('sort', 'newest')

    if category_id:
        sessions = sessions.filter(category__id=category_id)
    if session_type == 'regular':
        sessions = sessions.filter(is_pomodoro=False, is_countdown=False)
    elif session_type == 'pomodoro':
        sessions = sessions.filter(is_pomodoro=True)
    elif session_type == 'countdown':
        sessions = sessions.filter(is_countdown=True)

    if sort_by == 'oldest':
        sessions = sessions.order_by('start_time')
    elif sort_by == 'longest':
        sessions = sessions.order_by('-duration_seconds')
    elif sort_by == 'shortest':
        sessions = sessions.order_by('duration_seconds')
    else:
        sessions = sessions.order_by('-start_time')

    # Paginate
    paginator = Paginator(sessions, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Group by date
    from itertools import groupby
    grouped = []
    for date, group in groupby(page_obj, key=lambda s: s.start_time.date()):
        grouped.append({'date': date, 'sessions': list(group)})

    # Categories for filter dropdown
    categories = StudyCategory.objects.filter(user=request.user)

    today_total = StudySession.objects.filter(
        user=request.user, is_active=False, start_time__date=today
    ).aggregate(total=Sum('duration_seconds'))['total'] or 0

    return render(request, 'study/history.html', {
        'grouped_sessions': grouped,
        'page_obj': page_obj,
        'categories': categories,
        'total_count': paginator.count,
        'today_total': round(today_total / 3600, 2),
        'selected_category': category_id,
        'selected_type': session_type,
        'selected_sort': sort_by,
        'today': today,
        'yesterday': yesterday, 
    })

@login_required(login_url='planner:login')
def delete_session(request, session_id):
    """Delete a study session"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user)
    session.delete()
    return redirect('planner:study_history')


@login_required(login_url='planner:login')
def clear_all_history(request):
    """Delete all study sessions"""
    if request.method == 'POST':
        StudySession.objects.filter(user=request.user, is_active=False).delete()
        messages.success(request, "Study history cleared.")
    return redirect('planner:study_history')


@login_required(login_url='planner:login')
def study_statistics(request):
    """Statistics dashboard"""
    sessions = StudySession.objects.filter(user=request.user, is_active=False)
    today = timezone.now().date()

    total_sessions = sessions.count()
    total_seconds = sessions.aggregate(total=Sum('duration_seconds'))['total'] or 0
    total_hours = round(total_seconds / 3600, 2)
    current_streak = StudySession.get_user_streak(request.user)

    today_seconds = sessions.filter(start_time__date=today).aggregate(
        total=Sum('duration_seconds'))['total'] or 0
    week_start = today - timedelta(days=today.weekday())
    week_seconds = sessions.filter(start_time__date__gte=week_start).aggregate(
        total=Sum('duration_seconds'))['total'] or 0

    category_stats = sessions.values('category__name', 'category__color').annotate(
        total_seconds=Sum('duration_seconds'),
        session_count=Count('id')
    ).order_by('-total_seconds')

    category_stats_list = list(category_stats)
    for stat in category_stats_list:
        stat['total_hours'] = round(stat['total_seconds'] / 3600, 2)

    category_labels, category_data, category_colors = [], [], []
    for stat in category_stats_list:
        category_labels.append(stat['category__name'] or 'No Category')
        category_data.append(round(stat['total_seconds'] / 3600, 2))
        category_colors.append(stat['category__color'] or '#95a5a6')

    last_7_days, daily_data = [], []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        last_7_days.append(date.strftime('%b %d'))
        day_seconds = sessions.filter(start_time__date=date).aggregate(
            total=Sum('duration_seconds'))['total'] or 0
        daily_data.append(round(day_seconds / 3600, 2))

    return render(request, 'study/statistics.html', {
    'total_sessions': total_sessions,
    'total_hours': total_hours,
    'today_hours': round(today_seconds / 3600, 2),
    'week_hours': round(week_seconds / 3600, 2),
    'current_streak': current_streak,
    'category_labels': json.dumps(category_labels),
    'category_data': json.dumps(category_data),
    'category_colors': json.dumps(category_colors),
    'daily_labels': json.dumps(last_7_days),
    'daily_data': json.dumps(daily_data),
    'category_stats': category_stats_list,
})


@login_required(login_url='planner:login')
def study_streaks(request):
    from datetime import date, timedelta
    today = date.today()
    sessions = StudySession.objects.filter(user=request.user, is_active=False)
    study_dates = set(session.start_time.date() for session in sessions)

    # Build Sun–Sat week
    days_since_sunday = (today.weekday() + 1) % 7
    week_start = today - timedelta(days=days_since_sunday)

    week_days = []
    day_abbrs = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    days_studied_this_week = 0
    for i in range(7):
        d = week_start + timedelta(days=i)
        studied = d in study_dates
        if studied and d <= today:
            days_studied_this_week += 1
        week_days.append({
            'date': d,
            'abbr': day_abbrs[i],
            'studied': studied,
            'today': d == today,
            'future': d > today,
        })

    # Days elapsed this week (including today)
    days_elapsed = days_since_sunday + 1
    week_percentage = round((days_studied_this_week / days_elapsed) * 100) if days_elapsed > 0 else 0

    return render(request, 'study/streaks.html', {
        'current_streak': StudySession.get_user_streak(request.user),
        'longest_streak': StudySession.get_longest_streak(request.user),
        'total_study_days': len(study_dates),
        'week_days': week_days,
        'week_percentage': week_percentage,
    })


@login_required(login_url='planner:login')
def study_goals(request):
    """View and manage study goals"""
    active_goals = StudyGoal.objects.filter(user=request.user, is_active=True)
    inactive_goals = StudyGoal.objects.filter(user=request.user, is_active=False)

    goals_with_progress = [{'goal': g, 'progress': g.get_progress()} for g in active_goals]
    inactive_with_progress = [{'goal': g, 'progress': g.get_progress()} for g in inactive_goals]

    # Average completion across active goals
    avg_completion = 0
    if goals_with_progress:
        avg_completion = round(
            sum(item['progress']['percentage'] for item in goals_with_progress) / len(goals_with_progress)
        )

    return render(request, 'study/goals.html', {
        'goals_with_progress': goals_with_progress,
        'inactive_goals': inactive_with_progress,
        'avg_completion': avg_completion,
    })


@login_required(login_url='planner:login')
def add_goal(request):
    """Add a new study goal"""
    from ..forms import StudyGoalForm
    form = StudyGoalForm(request.POST or None, user=request.user)
    if form.is_valid():
        goal = form.save(commit=False)
        goal.user = request.user
        goal.save()
        messages.success(request, "Goal created successfully!")
        return redirect('planner:study_goals')
    return render(request, 'add_generic.html', {'form': form, 'title': 'Create Study Goal'})


@login_required(login_url='planner:login')
def edit_goal(request, goal_id):
    """Edit a study goal"""
    from ..forms import StudyGoalForm
    goal = get_object_or_404(StudyGoal, id=goal_id, user=request.user)
    form = StudyGoalForm(request.POST or None, instance=goal, user=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Goal updated successfully!")
        return redirect('planner:study_goals')
    return render(request, 'add_generic.html', {'form': form, 'title': 'Edit Study Goal'})


@login_required(login_url='planner:login')
def delete_goal(request, goal_id):
    """Delete a study goal"""
    goal = get_object_or_404(StudyGoal, id=goal_id, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, "Goal deleted successfully!")
        return redirect('planner:study_goals')
    return render(request, 'confirm_delete.html', {'object': goal, 'type': 'goal'})


@login_required(login_url='planner:login')
def toggle_goal(request, goal_id):
    """Toggle goal active status"""
    goal = get_object_or_404(StudyGoal, id=goal_id, user=request.user)
    goal.is_active = not goal.is_active
    goal.save()
    messages.success(request, f"Goal {'activated' if goal.is_active else 'deactivated'}!")
    return redirect('planner:study_goals')


@login_required(login_url='planner:login')
def manage_categories(request):
    """Manage study categories"""
    from django.db.models import Sum, Count
    categories = StudyCategory.objects.filter(user=request.user).annotate(
        total_sessions=Count('studysession'),
        total_hours=Sum('studysession__duration_seconds')
    )
    return render(request, 'study/categories.html', {
        'categories': categories,
    })


@login_required(login_url='planner:login')
def add_category(request):
    """Add a study category"""
    from ..forms import StudyCategoryForm
    form = StudyCategoryForm(request.POST or None)
    if form.is_valid():
        category = form.save(commit=False)
        category.user = request.user
        category.save()
        messages.success(request, "Category added!")
        return redirect('planner:manage_categories')
    return render(request, 'add_generic.html', {'form': form, 'title': 'Add Study Category'})


@login_required(login_url='planner:login')
def delete_category(request, category_id):
    """Delete a study category"""
    category = get_object_or_404(StudyCategory, id=category_id, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted!")
        return redirect('planner:manage_categories')
    return render(request, 'confirm_delete.html', {'object': category, 'type': 'category'})


@login_required(login_url='planner:login')
def suggest_subjects(request):
    """Suggest subjects from timetables"""
    user_timetables = Timetable.objects.filter(user=request.user)
    timetable_entries = TimetableEntry.objects.filter(timetable__in=user_timetables)

    subjects = set(entry.subjectInfo.subject for entry in timetable_entries)
    existing_categories = StudyCategory.objects.filter(user=request.user).values_list('name', flat=True)
    suggested_subjects = sorted([s for s in subjects if s not in existing_categories])

    return render(request, 'study/suggest_subjects.html', {
        'suggested_subjects': suggested_subjects,
        'existing_categories': existing_categories,
    })


@login_required(login_url='planner:login')
def quick_add_category(request, subject_name):
    """Quick add category from timetable subject"""
    if StudyCategory.objects.filter(user=request.user, name=subject_name).exists():
        messages.warning(request, f"Category '{subject_name}' already exists!")
    else:
        StudyCategory.objects.create(user=request.user, name=subject_name, color='#3498db')
        messages.success(request, f"Category '{subject_name}' created!")
    return redirect('planner:suggest_subjects')

@login_required(login_url='planner:login')
def bulk_add_categories(request):
    """Add all timetable subjects as categories"""
    if request.method == 'POST':
        user_timetables = Timetable.objects.filter(user=request.user)
        timetable_entries = TimetableEntry.objects.filter(timetable__in=user_timetables)
        subjects = set(entry.subjectInfo.subject for entry in timetable_entries)
        existing = set(StudyCategory.objects.filter(user=request.user).values_list('name', flat=True))

        added = 0
        for subject in subjects - existing:
            StudyCategory.objects.create(
                user=request.user,
                name=subject,
                color='#3498db'
            )
            added += 1

        if added > 0:
            messages.success(request, f"Added {added} new categories!")
        else:
            messages.info(request, "All subjects are already categories!")

    return redirect('planner:suggest_subjects')

@login_required(login_url='planner:login')
def pomodoro_timer(request):
    """Pomodoro timer page"""
    categories = StudyCategory.objects.filter(user=request.user)
    active_session = StudySession.objects.filter(
        user=request.user,
        is_active=True,
        is_pomodoro=True
    ).first()

    # Ring color shifts darker with each completed pomodoro
    ring_colors = ['#C4714A', '#8B4A2F', '#5C2E18', '#422a20']
    ring_color = '#C4714A'
    if active_session:
        idx = min(active_session.pomodoros_completed, len(ring_colors) - 1)
        ring_color = ring_colors[idx]

    return render(request, 'study/pomodoro.html', {
        'categories': categories,
        'active_session': active_session,
        'ring_color': ring_color,
    })


@login_required(login_url='planner:login')
def start_pomodoro(request):
    """Start a pomodoro session"""
    if request.method == 'POST':
        category_id = request.POST.get('category')
        category = None
        if category_id:
            category = StudyCategory.objects.get(id=category_id, user=request.user)

        if StudySession.objects.filter(user=request.user, is_active=True).exists():
            messages.warning(request, "You already have an active session!")
            return redirect('planner:pomodoro_timer')

        StudySession.objects.create(
            user=request.user,
            category=category,
            start_time=timezone.now(),
            is_active=True,
            is_pomodoro=True
        )
        messages.success(request, "Pomodoro started!")
    return redirect('planner:pomodoro_timer')


@login_required(login_url='planner:login')
def pause_pomodoro(request, session_id):
    """Pause an active pomodoro session"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user, is_active=True, is_pomodoro=True)
    if not session.is_paused:
        session.is_paused = True
        session.pause_start = timezone.now()
        session.save()
        messages.success(request, "Pomodoro paused")
    return redirect('planner:pomodoro_timer')


@login_required(login_url='planner:login')
def resume_pomodoro(request, session_id):
    """Resume a paused pomodoro session"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user, is_active=True, is_pomodoro=True)
    if session.is_paused and session.pause_start:
        pause_duration = int((timezone.now() - session.pause_start).total_seconds())
        session.paused_seconds += pause_duration
        session.is_paused = False
        session.pause_start = None
        session.save()
        messages.success(request, "Pomodoro resumed")
    return redirect('planner:pomodoro_timer')


@login_required(login_url='planner:login')
def complete_pomodoro(request, session_id):
    """Complete a pomodoro (mark one 25-min block done)"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user, is_active=True, is_pomodoro=True)
    if session.is_paused and session.pause_start:
        pause_duration = int((timezone.now() - session.pause_start).total_seconds())
        session.paused_seconds += pause_duration
        session.is_paused = False
        session.pause_start = None
    session.duration_seconds += 1500
    session.pomodoros_completed += 1
    session.save()
    messages.success(request, f"Pomodoro #{session.pomodoros_completed} completed! Take a break.")
    return redirect('planner:pomodoro_timer')


@login_required(login_url='planner:login')
def stop_pomodoro(request, session_id):
    """Stop a pomodoro session"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user, is_active=True, is_pomodoro=True)
    session.end_time = timezone.now()
    if session.is_paused and session.pause_start:
        pause_duration = int((timezone.now() - session.pause_start).total_seconds())
        session.paused_seconds += pause_duration
    elapsed = int((session.end_time - session.start_time).total_seconds())
    partial_time = elapsed - session.paused_seconds - (session.pomodoros_completed * 1500)
    session.duration_seconds += max(partial_time, 0)
    session.is_active = False
    session.is_paused = False
    session.save()
    messages.success(request, f"Session ended! {session.pomodoros_completed} pomodoros completed.")
    return redirect('planner:pomodoro_timer')


@login_required(login_url='planner:login')
def study_resources(request):
    """View all study resources"""
    resources = StudyResource.objects.filter(user=request.user)
    categories = StudyCategory.objects.filter(user=request.user)
    
    # Filter by category if requested
    category_id = request.GET.get('category')
    if category_id:
        resources = resources.filter(category_id=category_id)
    
    return render(request, 'study/resources.html', {
        'resources': resources,
        'categories': categories,
        'selected_category': category_id
    })


@login_required(login_url='planner:login')
def add_resource(request):
    """Add a new study resource"""
    form = StudyResourceForm(request.POST or None, user=request.user)
    if form.is_valid():
        resource = form.save(commit=False)
        resource.user = request.user
        resource.save()
        messages.success(request, "Resource added successfully!")
        return redirect('planner:study_resources')
    return render(request, 'add_generic.html', {'form': form, 'title': 'Add Study Resource'})


@login_required(login_url='planner:login')
def edit_resource(request, resource_id):
    """Edit a study resource"""
    resource = get_object_or_404(StudyResource, id=resource_id, user=request.user)
    form = StudyResourceForm(request.POST or None, instance=resource, user=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Resource updated successfully!")
        return redirect('planner:study_resources')
    return render(request, 'add_generic.html', {'form': form, 'title': 'Edit Resource'})


@login_required(login_url='planner:login')
def delete_resource(request, resource_id):
    """Delete a study resource"""
    resource = get_object_or_404(StudyResource, id=resource_id, user=request.user)
    if request.method == 'POST':
        resource.delete()
        messages.success(request, "Resource deleted successfully!")
        return redirect('planner:study_resources')
    return render(request, 'confirm_delete.html', {'object': resource, 'type': 'resource'})


def get_today_study_hours(user):
    from django.utils import timezone
    today = timezone.now().date()
    total_seconds = StudySession.objects.filter(
        user=user,
        is_active=False,
        start_time__date=today
    ).aggregate(total=Sum('duration_seconds'))['total'] or 0
    return round(total_seconds / 3600, 2)


@login_required(login_url='planner:login')
def start_countdown(request):
    """Start a countdown timer session"""
    if request.method == 'POST':
        category_id = request.POST.get('category')
        hours = int(request.POST.get('hours', 0) or 0)
        minutes = int(request.POST.get('minutes', 0) or 0)
        target_seconds = (hours * 3600) + (minutes * 60)

        if target_seconds <= 0:
            messages.error(request, "Please set a valid duration.")
            return redirect('planner:study_timer')

        if StudySession.objects.filter(user=request.user, is_active=True).exists():
            messages.warning(request, "You already have an active session!")
            return redirect('planner:study_timer')

        category = None
        if category_id:
            category = StudyCategory.objects.get(id=category_id, user=request.user)

        StudySession.objects.create(
            user=request.user,
            category=category,
            start_time=timezone.now(),
            is_active=True,
            is_countdown=True,
            countdown_target_seconds=target_seconds
        )
        messages.success(request, "Countdown started!")
    return redirect('planner:study_timer')


# countdown timer
@login_required(login_url='planner:login')
def stop_countdown(request, session_id):
    """Stop a countdown session"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user, is_active=True, is_countdown=True)
    session.end_time = timezone.now()
    elapsed = int((session.end_time - session.start_time).total_seconds())
    if session.is_paused and session.pause_start:
        pause_duration = int((timezone.now() - session.pause_start).total_seconds())
        session.paused_seconds += pause_duration
    session.duration_seconds = max(elapsed - session.paused_seconds, 0)
    session.is_active = False
    session.is_paused = False
    session.save()
    messages.success(request, f"Countdown ended! Studied for {session.get_duration_display()}")
    return redirect('planner:study_timer')


@login_required(login_url='planner:login')
def complete_countdown(request, session_id):
    """Mark countdown as naturally completed (reached zero)"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user, is_active=True, is_countdown=True)
    session.end_time = timezone.now()
    session.duration_seconds = session.countdown_target_seconds
    session.is_active = False
    session.is_paused = False
    session.save()
    messages.success(request, "Countdown complete! Great work.")
    return redirect('planner:study_timer')