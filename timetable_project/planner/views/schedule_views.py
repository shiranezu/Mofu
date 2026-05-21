import calendar
import json
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import ScheduleEntry
from ..forms import ScheduleEntryForm


@login_required(login_url='planner:login')
def schedule_home(request):
    """Main calendar view"""
    today = timezone.now().date()

    # Determine which month to show
    month_str = request.GET.get('month')
    if month_str:
        try:
            year, month = int(month_str.split('-')[0]), int(month_str.split('-')[1])
        except Exception:
            year, month = today.year, today.month
    else:
        year, month = today.year, today.month

    # Build calendar grid (weeks × days)
    cal = calendar.Calendar(firstweekday=6)  # Sunday first
    month_days = cal.monthdatescalendar(year, month)

    # Fetch all entries for this month (include days from adjacent months shown in grid)
    grid_start = month_days[0][0]
    grid_end = month_days[-1][-1]
    entries = ScheduleEntry.objects.filter(
        user=request.user,
        date__gte=grid_start,
        date__lte=grid_end
    )

    # Build a dict: date_str -> list of entry dicts (for JS)
    entries_by_date = {}
    for entry in entries:
        key = entry.date.isoformat()
        if key not in entries_by_date:
            entries_by_date[key] = []
        entries_by_date[key].append({
            'id': entry.id,
            'title': entry.title,
            'start_time': entry.start_time.strftime('%H:%M') if entry.start_time else '',
            'end_time': entry.end_time.strftime('%H:%M') if entry.end_time else '',
            'description': entry.description or '',
            'is_done': entry.is_done,
        })

    # Prev / next month
    first_of_month = date(year, month, 1)
    prev_month = (first_of_month - timedelta(days=1)).replace(day=1)
    next_month = (first_of_month + timedelta(days=32)).replace(day=1)

    # Selected date (from query param, default today)
    selected_str = request.GET.get('date', today.isoformat())

    context = {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'month_days': month_days,
        'today': today,
        'prev_month': prev_month.strftime('%Y-%m'),
        'next_month': next_month.strftime('%Y-%m'),
        'entries_json': json.dumps(entries_by_date),
        'selected_date': selected_str,
        'dow_headers': ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
    }
    return render(request, 'schedule.html', context)


@login_required(login_url='planner:login')
def add_schedule_entry(request):
    date_str = request.GET.get('date') or request.POST.get('date') or timezone.now().date().isoformat()
    initial = {'date': date_str}
    form = ScheduleEntryForm(request.POST or None, initial=initial)
    if form.is_valid():
        entry = form.save(commit=False)
        entry.user = request.user
        entry.save()
        from django.urls import reverse
        return redirect(reverse('planner:schedule_home') + f"?date={entry.date.isoformat()}&month={entry.date.strftime('%Y-%m')}")
    return render(request, 'add_generic.html', {'form': form, 'title': 'Add Schedule Entry'})


@login_required(login_url='planner:login')
def view_schedule_entry(request, entry_id):
    entry = get_object_or_404(ScheduleEntry, id=entry_id, user=request.user)
    return render(request, 'schedule_entry.html', {'entry': entry})


@login_required(login_url='planner:login')
def edit_schedule_entry(request, entry_id):
    entry = get_object_or_404(ScheduleEntry, id=entry_id, user=request.user)
    form = ScheduleEntryForm(request.POST or None, instance=entry)
    if form.is_valid():
        form.save()
        return redirect(f"/schedule/?date={entry.date.isoformat()}&month={entry.date.strftime('%Y-%m')}")
    return render(request, 'add_generic.html', {'form': form, 'title': 'Edit Schedule Entry'})


@login_required(login_url='planner:login')
def delete_schedule_entry(request, entry_id):
    entry = get_object_or_404(ScheduleEntry, id=entry_id, user=request.user)
    date_str = entry.date.isoformat()
    month_str = entry.date.strftime('%Y-%m')
    if request.method == 'POST':
        entry.delete()
        return redirect(f"/schedule/?date={date_str}&month={month_str}")
    return render(request, 'confirm_delete.html', {'object': entry, 'type': 'schedule entry'})


@login_required(login_url='planner:login')
def toggle_schedule_entry(request, entry_id):
    entry = get_object_or_404(ScheduleEntry, id=entry_id, user=request.user)
    entry.is_done = not entry.is_done
    entry.save()
    return redirect(f"/schedule/?date={entry.date.isoformat()}&month={entry.date.strftime('%Y-%m')}")