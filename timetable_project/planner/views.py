from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from .models import Timetable, TimetableEntry, Timeslot, Schedule, ScheduleItem
from .forms import Subject_and_locationForm, RegistrationForm, TimeslotForm, ScheduleForm, ScheduleItemForm
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from django.http import HttpResponse


# Timetable Views
@login_required(login_url='planner:login')
def timetable_view(request, timetable_id):
    timetable = get_object_or_404(Timetable, id=timetable_id, user=request.user)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    timeslots = Timeslot.objects.all().order_by('start_time')

    grid = []
    for day in days:
        row = []
        for timeslot in timeslots:
            entry = TimetableEntry.objects.filter(
                timetable=timetable,
                day=day,
                timeslot=timeslot
            ).first()
            row.append((entry, timeslot))  # ✅ store both
        grid.append((day, row))

    context = {
        'timetable': timetable,
        'grid': grid,
        'timeslots': timeslots
    }
    return render(request, 'index.html', context)


@login_required(login_url='planner:login')
def edit_view(request):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    timeslots = Timeslot.objects.all().order_by('start_time')
    
    grid = []
    for day in days:
        row = []
        for timeslot in timeslots:
            entry = TimetableEntry.objects.filter(day=day, timeslot=timeslot).first()
            row.append(entry)
        grid.append((day, row))

    context = {
        'grid': grid,
        'timeslots': timeslots
    }
    return render(request, 'edit.html', context)


@login_required(login_url='planner:login')
def add_course(request):
    timetable_id = request.GET.get('timetable') or request.POST.get('timetable')
    timetable = get_object_or_404(Timetable, id=timetable_id, user=request.user)

    day = request.GET.get('day')  # pre-fill
    timeslot_id = request.GET.get('timeslot')

    form = Subject_and_locationForm(request.POST or None)

    if form.is_valid():
        course = form.save()
        timeslot = Timeslot.objects.get(id=request.POST.get('timeslot'))
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
        form.save()
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
    timeslot = Timeslot.objects.filter(id=timeslot_id).first()
    if not timeslot:
        messages.error(request, "This timeslot does not exist or was already deleted.")
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

# Authentication Views
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == '':
            return render(request, 'auth/login.html')
        elif password == '':
            return render(request, 'auth/login.html')
        user = authenticate(username = username, password = password)
        if user:
            login(request, user)
            return redirect('planner:home')
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
    