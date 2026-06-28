from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from ..models import Timetable, TimetableEntry, Timeslot, StudyCategory
from ..forms import Subject_and_locationForm, TimeslotForm, TimetableForm


@login_required(login_url='planner:login')
def timetable_home(request):
    """View all timetables"""
    timetables = Timetable.objects.filter(user=request.user)
    return render(request, 'timetable_home.html', {'timetables': timetables})


WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
FULL_WEEK = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
@login_required(login_url='planner:login')
def timetable_view(request, timetable_id):
    timetable = get_object_or_404(Timetable, id=timetable_id, user=request.user)
    days = FULL_WEEK if timetable.days_mode == 'full_week' else WEEKDAYS
    timeslots = Timeslot.objects.filter(timetable=timetable).order_by('start_time')
    all_timetables = Timetable.objects.filter(user=request.user)
    today_day = timezone.now().strftime('%A')

    # Desktop grid: rows = days, cols = timeslots
    grid = []
    entry_map = {}
    for day in days:
        row = []
        for timeslot in timeslots:
            entry = TimetableEntry.objects.filter(
                timetable=timetable,
                day=day,
                timeslot=timeslot
            ).first()
            row.append((entry, timeslot))
            entry_map[(day, timeslot.id)] = entry
        grid.append((day, row))

    # Mobile grid: rows = timeslots, cols = days
    mobile_grid = []
    for timeslot in timeslots:
        row = []
        for day in days:
            entry = entry_map.get((day, timeslot.id))
            row.append((day, entry))
        mobile_grid.append((timeslot, row))

    # Collect categories used in this timetable for the legend
    category_ids = TimetableEntry.objects.filter(
        timetable=timetable
    ).exclude(
        subjectInfo__category=None
    ).values_list('subjectInfo__category', flat=True).distinct()
    categories_used = StudyCategory.objects.filter(id__in=category_ids)

    return render(request, 'index.html', {
        'timetable': timetable,
        'grid': grid,
        'mobile_grid': mobile_grid,
        'days': days,
        'timeslots': timeslots,
        'all_timetables': all_timetables,
        'today_day': today_day,
        'categories_used': categories_used,
    })

@login_required(login_url='planner:login')
def create_timetable(request):
    form = TimetableForm(request.POST or None)
    if form.is_valid():
        timetable = form.save(commit=False)
        timetable.user = request.user
        timetable.save()
        return redirect('planner:timetable_home')
    return render(request, 'add_generic.html', {
        'form': form,
        'title': 'Create Timetable'
    })


@login_required(login_url='planner:login')
def delete_timetable(request, timetable_id):
    """Delete a timetable"""
    timetable = Timetable.objects.filter(id=timetable_id, user=request.user).first()

    if not timetable:
        messages.error(request, "This timetable does not exist or was already deleted.")
        return redirect('planner:timetable_home')

    if request.method == "POST":
        timetable.delete()
        messages.success(request, "Timetable deleted successfully.")
        return redirect('planner:timetable_home')

    return render(request, 'confirm_delete.html', {
        'object': timetable,
        'type': 'timetable'
    })


@login_required(login_url='planner:login')
def add_course(request):
    """Add a course to a timetable"""
    timetable_id = request.GET.get('timetable') or request.POST.get('timetable')
    timetable = get_object_or_404(Timetable, id=timetable_id, user=request.user)

    day = request.GET.get('day')
    timeslot_id = request.GET.get('timeslot')
    form = Subject_and_locationForm(request.POST or None, user=request.user, timetable=timetable)  # Changed

    if form.is_valid():
        course = form.save()
        timeslot = Timeslot.objects.get(id=request.POST.get('timeslot'), timetable=timetable)
        TimetableEntry.objects.create(
            timetable=timetable,
            day=request.POST.get('day'),
            timeslot=timeslot,
            subjectInfo=course
        )
        return redirect('planner:timetable_view', timetable_id=timetable.id)

    return render(request, 'add_generic.html', {
        'form': form,
        'title': 'Add Course',
        'timetable': timetable,
        'day': day,
        'timeslot_id': timeslot_id
    })


@login_required(login_url='planner:login')
def add_timeslot(request):
    """Add a timeslot"""
    timetable_id = request.GET.get('timetable') or request.POST.get('timetable')
    
    if not timetable_id:
        messages.error(request, "No timetable specified!")
        return redirect('planner:timetable_home')
    
    timetable = get_object_or_404(Timetable, id=timetable_id, user=request.user)
    
    form = TimeslotForm(request.POST or None)
    if form.is_valid():
        timeslot = form.save(commit=False)
        timeslot.timetable = timetable 
        timeslot.save()
        return redirect('planner:timetable_view', timetable_id=timetable.id)
    
    return render(request, 'add_generic.html', {
        'form': form,
        'title': 'Add Timeslot',
        'timetable': timetable
    })


@login_required(login_url='planner:login')
def edit_entry(request, entry_id):
    """Edit a timetable entry"""
    entry = TimetableEntry.objects.filter(id=entry_id, timetable__user=request.user).first()
    if not entry:
        messages.error(request, "This entry does not exist.")
        return redirect('planner:timetable_home')

    form = Subject_and_locationForm(request.POST or None, instance=entry.subjectInfo)
    if form.is_valid():
        form.save()
        messages.success(request, "Entry updated successfully.")
        return redirect('planner:timetable_view', timetable_id=entry.timetable.id)

    return render(request, 'add_generic.html', {'form': form, 'title': 'Edit Entry'})


@login_required(login_url='planner:login')
def delete_entry(request, entry_id):
    """Delete a timetable entry"""
    entry = TimetableEntry.objects.filter(id=entry_id, timetable__user=request.user).first()
    if not entry:
        messages.error(request, "This entry does not exist or was already deleted.")
        return redirect('planner:timetable_home')

    timetable_id = entry.timetable.id
    entry.delete()
    messages.success(request, "Entry deleted successfully.")
    return redirect('planner:timetable_view', timetable_id=timetable_id)


@login_required(login_url='planner:login')
def delete_timeslot(request, timeslot_id):
    """Delete a timeslot"""
    timeslot = Timeslot.objects.filter(id=timeslot_id, timetable__user=request.user).first()  # Changed
    
    if not timeslot:
        messages.error(request, "This timeslot does not exist or you don't have permission.")
        return redirect('planner:timetable_home')

    timetable_id = timeslot.timetable.id  # Save timetable id before deleting
    
    if request.method == "POST":
        timeslot.delete()
        messages.success(request, "Timeslot deleted successfully.")
        return redirect('planner:timetable_view', timetable_id=timetable_id)  # Return to timetable

    return render(request, 'confirm_delete.html', {
        'object': timeslot,
        'type': 'timeslot'
    })


@login_required(login_url='planner:login')
def export_timetable_pdf(request, timetable_id):
    """Export timetable as PDF"""
    timetable = get_object_or_404(Timetable, id=timetable_id, user=request.user)
    timeslots = Timeslot.objects.filter(timetable=timetable).order_by('start_time')
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    entries = TimetableEntry.objects.filter(timetable=timetable)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{timetable.name}.pdf"'

    p = canvas.Canvas(response, pagesize=landscape(letter))
    width, height = landscape(letter)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(30, height - 30, f"Timetable: {timetable.name}")

    x_start, y_start = 50, height - 70
    cell_width, cell_height = 120, 30

    p.setFont("Helvetica-Bold", 10)
    p.drawString(x_start, y_start, "Day/Time")
    for i, slot in enumerate(timeslots):
        p.drawString(x_start + (i+1)*cell_width, y_start, f"{slot.start_time}-{slot.end_time}")

    y = y_start - cell_height
    p.setFont("Helvetica", 9)
    for day in days:
        p.drawString(x_start, y, day)
        for i, slot in enumerate(timeslots):
            entry = entries.filter(day=day, timeslot=slot).first()
            text = entry.subjectInfo.subject if entry else ""
            p.drawString(x_start + (i+1)*cell_width, y, text)
        y -= cell_height

    p.showPage()
    p.save()
    return response


@login_required(login_url='planner:login')
def toggle_days_mode(request, timetable_id):
    """Toggle timetable between weekdays and full week"""
    timetable = get_object_or_404(Timetable, id=timetable_id, user=request.user)
    timetable.days_mode = 'full_week' if timetable.days_mode == 'weekdays' else 'weekdays'
    timetable.save()
    return redirect('planner:timetable_view', timetable_id=timetable_id)