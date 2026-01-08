from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from .models import Timetable, TimetableEntry, Timeslot, Schedule, ScheduleItem, StudyCategory, StudySession
from .forms import Subject_and_locationForm, RegistrationForm, TimeslotForm, ScheduleForm, ScheduleItemForm, StudyCategoryForm, StudySessionForm
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta



# Timetable Views
@login_required(login_url='planner:login')
def timetable_view(request, timetable_id):
    timetable = get_object_or_404(Timetable, id=timetable_id, user=request.user)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    timeslots = Timeslot.objects.filter(user=request.user).order_by('start_time')

    grid = []
    for day in days:
        row = []
        for timeslot in timeslots:
            entry = TimetableEntry.objects.filter(
                timetable=timetable,
                day=day,
                timeslot=timeslot
            ).first()
            row.append((entry, timeslot))
        grid.append((day, row))

    context = {
        'timetable': timetable,
        'grid': grid,
        'timeslots': timeslots
    }
    return render(request, 'index.html', context)


@login_required(login_url='planner:login')
def add_course(request):
    timetable_id = request.GET.get('timetable') or request.POST.get('timetable')
    timetable = get_object_or_404(Timetable, id=timetable_id, user=request.user)

    day = request.GET.get('day')
    timeslot_id = request.GET.get('timeslot')

    form = Subject_and_locationForm(request.POST or None, user=request.user)

    if form.is_valid():
        course = form.save()
        timeslot = Timeslot.objects.get(id=request.POST.get('timeslot'), user=request.user)
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
    form = TimeslotForm(request.POST or None)
    if form.is_valid():
        timeslot = form.save(commit=False)
        timeslot.user = request.user
        timeslot.save()
        return redirect('planner:home')
    else:
        print(form.errors)
    return render(request, 'add_generic.html', {'form': form, 'title': 'Add Timeslot'})


@login_required(login_url='planner:login')
def edit_entry(request, entry_id):
    entry = TimetableEntry.objects.filter(id=entry_id, timetable__user=request.user).first()
    if not entry:
        messages.error(request, "This entry does not exist.")
        return redirect('planner:select_timetable')

    form = Subject_and_locationForm(request.POST or None, instance=entry.subjectInfo)

    if form.is_valid():
        form.save()
        messages.success(request, "Entry updated successfully.")
        return redirect('planner:timetable_view', timetable_id=entry.timetable.id)

    return render(request, 'add_generic.html', {'form': form, 'title': 'Edit Entry'})


@login_required(login_url='planner:login')
def delete_entry(request, entry_id):
    entry = TimetableEntry.objects.filter(id=entry_id, timetable__user=request.user).first()
    if not entry:
        messages.error(request, "This entry does not exist or was already deleted.")
        return redirect('planner:select_timetable')

    timetable_id = entry.timetable.id
    entry.delete()
    messages.success(request, "Entry deleted successfully.")
    return redirect('planner:timetable_view', timetable_id=timetable_id)


@login_required(login_url='planner:login')
def create_timetable(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        Timetable.objects.create(user=request.user, name=name)
        return redirect('planner:home')
    return render(request, 'create_timetable.html')


@login_required(login_url='planner:login')
def select_timetable(request):
    timetables = Timetable.objects.filter(user=request.user)
    schedules = Schedule.objects.filter(user=request.user)
    return render(request, "select_timetable.html", {
        "timetables": timetables,
        "schedules": schedules
    })


@login_required(login_url='planner:login')
def delete_timetable(request, timetable_id):
    timetable = Timetable.objects.filter(id=timetable_id, user=request.user).first()

    if not timetable:
        messages.error(request, "This timetable does not exist or was already deleted.")
        return redirect('planner:home')

    if request.method == "POST":
        timetable.delete()
        messages.success(request, "Timetable deleted successfully.")
        return redirect('planner:home')

    return render(request, 'confirm_delete.html', {
        'object': timetable,
        'type': 'timetable'
    })


@login_required
def delete_timeslot(request, timeslot_id):
    timeslot = Timeslot.objects.filter(id=timeslot_id, user=request.user).first()
    if not timeslot:
        messages.error(request, "This timeslot does not exist or you don't have permission to delete it.")
        return redirect('planner:home')

    if request.method == "POST":
        timeslot.delete()
        messages.success(request, "Timeslot deleted successfully.")
        return redirect('planner:home')

    return render(request, 'confirm_delete.html', {
        'object': timeslot,
        'type': 'timeslot'
    })


@login_required(login_url='planner:login')
def export_timetable_pdf(request, timetable_id):
    timetable = get_object_or_404(Timetable, id=timetable_id, user=request.user)
    timeslots = Timeslot.objects.all().order_by('start_time')
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    entries = TimetableEntry.objects.filter(timetable=timetable)

    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{timetable.name}.pdf"'

    # Create PDF canvas
    p = canvas.Canvas(response, pagesize=landscape(letter))
    width, height = landscape(letter)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(30, height - 30, f"Timetable: {timetable.name}")

    # Draw grid headers
    x_start, y_start = 50, height - 70
    cell_width, cell_height = 120, 30

    # Header row (timeslots)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(x_start, y_start, "Day/Time")
    for i, slot in enumerate(timeslots):
        p.drawString(x_start + (i+1)*cell_width, y_start, f"{slot.start_time}-{slot.end_time}")

    # Rows (days + entries)
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

# Schedule Views


@login_required(login_url='planner:login')
def select_schedule(request):
    return redirect('planner:home')
    # schedules = Schedule.objects.filter(user=request.user)
    # return render(request, "select_timetable.html", {"schedules": schedules})


@login_required(login_url='planner:login')
def schedule_view(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)
    items = schedule.items.all().order_by("due_date", "id")
    return render(request, "schedule_view.html", {"schedule": schedule, "items": items})


@login_required(login_url='planner:login')
def create_schedule(request):
    form = ScheduleForm(request.POST or None)
    if form.is_valid():
        schedule = form.save(commit=False)
        schedule.user = request.user
        schedule.save()
        return redirect("planner:schedule_view", schedule.id)
    return render(request, "add_generic.html", {"form": form, "title": "Create Schedule"})


@login_required(login_url='planner:login')
def add_schedule_item(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)
    form = ScheduleItemForm(request.POST or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.schedule = schedule
        item.save()
        return redirect("planner:schedule_view", schedule.id)
    return render(request, "add_generic.html", {"form": form, "title": "Add Task"})


@login_required(login_url='planner:login')
def edit_schedule_item(request, item_id):
    item = get_object_or_404(ScheduleItem, id=item_id, schedule__user=request.user)
    form = ScheduleItemForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect("planner:schedule_view", item.schedule.id)
    return render(request, "add_generic.html", {"form": form, "title": "Edit Task"})


@login_required(login_url='planner:login')
def delete_schedule_item(request, item_id):
    item = get_object_or_404(ScheduleItem, id=item_id, schedule__user=request.user)
    schedule_id = item.schedule.id
    item.delete()
    return redirect("planner:schedule_view", schedule_id)


@login_required(login_url='planner:login')
def delete_schedule(request, schedule_id):
    schedule = Schedule.objects.filter(id=schedule_id, user=request.user).first()
    if not schedule:
        messages.error(request, "This schedule does not exist or was already deleted.")
        return redirect('planner:home')

    if request.method == "POST":
        schedule.delete()
        messages.success(request, "Schedule deleted successfully.")
        return redirect('planner:home')

    return render(request, 'confirm_delete.html', {
        'object': schedule,
        'type': 'schedule'
    })


@login_required(login_url='planner:login')
def toggle_schedule_item(request, item_id):
    item = get_object_or_404(ScheduleItem, id=item_id, schedule__user=request.user)
    item.is_done = not item.is_done
    item.save()
    return redirect("planner:schedule_view", item.schedule.id)


@login_required
def export_schedule_pdf(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)
    items = schedule.items.all().order_by("id")

    # Create HTTP response with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{schedule.name}.pdf"'

    # Create PDF canvas
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Schedule: {schedule.name}")

    # Task list
    y = height - 100
    p.setFont("Helvetica", 12)
    for item in items:
        status = "[x]" if item.is_done else "[ ]"
        line = f"{status} {item.title}"
        p.drawString(60, y, line)
        y -= 20

        if y < 50:  # New page if space runs out
            p.showPage()
            y = height - 50

    p.showPage()
    p.save()
    return response 

# study timer
@login_required(login_url='planner:login')
def study_timer(request):
    """Main timer page"""
    categories = StudyCategory.objects.filter(user=request.user)
    active_session = StudySession.objects.filter(user=request.user, is_active=True).first()
    
    context = {
        'categories': categories,
        'active_session': active_session,
    }
    return render(request, 'study/timer.html', context)


@login_required(login_url='planner:login')
def start_timer(request):
    """Start a new study session"""
    if request.method == 'POST':
        category_id = request.POST.get('category')
        category = None
        if category_id:
            category = StudyCategory.objects.get(id=category_id, user=request.user)
        
        # Check if there's already an active session
        active_session = StudySession.objects.filter(user=request.user, is_active=True).first()
        if active_session:
            messages.warning(request, "You already have an active study session!")
            return redirect('planner:study_timer')
        
        # Create new session
        StudySession.objects.create(
            user=request.user,
            category=category,
            start_time=timezone.now(),
            is_active=True
        )
        messages.success(request, "Study session started!")
        return redirect('planner:study_timer')
    
    return redirect('planner:study_timer')


@login_required(login_url='planner:login')
def stop_timer(request, session_id):
    """Stop and save study session"""
    session = get_object_or_404(StudySession, id=session_id, user=request.user, is_active=True)
    
    session.end_time = timezone.now()
    session.duration_seconds = int((session.end_time - session.start_time).total_seconds())
    session.is_active = False
    session.save()
    
    messages.success(request, f"Study session completed! Duration: {session.get_duration_display()}")
    return redirect('planner:study_timer')


@login_required(login_url='planner:login')
def study_history(request):
    """View all past study sessions"""
    sessions = StudySession.objects.filter(user=request.user, is_active=False)
    
    # Calculate statistics
    today = timezone.now().date()
    today_sessions = sessions.filter(start_time__date=today)
    today_total = today_sessions.aggregate(total=Sum('duration_seconds'))['total'] or 0
    
    week_start = today - timedelta(days=today.weekday())
    week_sessions = sessions.filter(start_time__date__gte=week_start)
    week_total = week_sessions.aggregate(total=Sum('duration_seconds'))['total'] or 0
    
    context = {
        'sessions': sessions,
        'today_total': today_total,
        'week_total': week_total,
    }
    return render(request, 'study/history.html', context)


@login_required(login_url='planner:login')
def manage_categories(request):
    """Manage study categories"""
    categories = StudyCategory.objects.filter(user=request.user)
    return render(request, 'study/categories.html', {'categories': categories})


@login_required(login_url='planner:login')
def add_category(request):
    """Add a new study category"""
    form = StudyCategoryForm(request.POST or None)
    if form.is_valid():
        category = form.save(commit=False)
        category.user = request.user
        category.save()
        messages.success(request, "Category added successfully!")
        return redirect('planner:manage_categories')
    
    return render(request, 'add_generic.html', {'form': form, 'title': 'Add Study Category'})


@login_required(login_url='planner:login')
def delete_category(request, category_id):
    """Delete a study category"""
    category = get_object_or_404(StudyCategory, id=category_id, user=request.user)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully!")
        return redirect('planner:manage_categories')
    
    return render(request, 'confirm_delete.html', {
        'object': category,
        'type': 'category'
    })


# Authentication Views
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username:
            messages.error(request, 'Please enter a username.')
            return render(request, 'auth/login.html')
        
        if not password:
            messages.error(request, 'Please enter a password.')
            return render(request, 'auth/login.html')
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('planner:home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')

def register(request):
    form = RegistrationForm
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('planner:login')
    return render(request, 'auth/register.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('planner:login')

# Other views

@login_required(login_url='planner:login')
def help(request):
    return render(request, 'help.html')

# @login_required(login_url='planner:login')
# def chatbot(request):