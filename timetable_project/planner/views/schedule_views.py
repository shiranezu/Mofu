from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from ..models import Schedule, ScheduleItem
from ..forms import ScheduleForm, ScheduleItemForm


@login_required(login_url='planner:login')
def schedule_home(request):
    """View all schedules"""
    schedules = Schedule.objects.filter(user=request.user)
    
    schedules_data = []
    for schedule in schedules:
        total = schedule.items.count()
        completed = schedule.items.filter(status='completed').count()
        pending = total - completed
        percentage = int((completed / total * 100)) if total > 0 else 0
        schedules_data.append({
            'schedule': schedule,
            'total': total,
            'completed': completed,
            'pending': pending,
            'percentage': percentage,
        })
    
    return render(request, 'schedule_home.html', {
        'schedules_data': schedules_data,
        'schedules': schedules,
    })


@login_required(login_url='planner:login')
def schedule_view(request, schedule_id):
    """View a specific schedule"""
    schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)
    items = schedule.items.all().order_by("due_date", "id")
    
    from django.utils import timezone
    today = timezone.now().date()
    
    return render(request, "schedule_view.html", {
        "schedule": schedule, 
        "items": items,
        "today": today
    })

@login_required(login_url='planner:login')
def quick_add_task(request):
    """Quick add task from Today page"""
    if request.method == 'POST':
        title = request.POST.get('title')
        priority = request.POST.get('priority', 'medium')
        due_date = request.POST.get('due_date')
        
        # Get or create a default "Quick Tasks" schedule
        schedule, created = Schedule.objects.get_or_create(
            user=request.user,
            name="Quick Tasks"
        )
        
        ScheduleItem.objects.create(
            schedule=schedule,
            title=title,
            priority=priority,
            due_date=due_date if due_date else None,
            status='not_started'
        )
        
        messages.success(request, f"Task '{title}' added!")
    
    return redirect('planner:home')


@login_required(login_url='planner:login')
def create_schedule(request):
    """Create a new schedule"""
    form = ScheduleForm(request.POST or None)
    if form.is_valid():
        schedule = form.save(commit=False)
        schedule.user = request.user
        schedule.save()
        return redirect("planner:schedule_view", schedule.id)
    return render(request, "add_generic.html", {"form": form, "title": "Create Schedule"})


@login_required(login_url='planner:login')
def add_schedule_item(request, schedule_id):
    """Add an item to a schedule"""
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
    """Edit a schedule item"""
    item = get_object_or_404(ScheduleItem, id=item_id, schedule__user=request.user)
    form = ScheduleItemForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect("planner:schedule_view", item.schedule.id)
    return render(request, "add_generic.html", {"form": form, "title": "Edit Task"})


@login_required(login_url='planner:login')
def view_schedule_item(request, item_id):
    """View a schedule item"""
    item = get_object_or_404(ScheduleItem, id=item_id, schedule__user=request.user)
    return render(request, 'view_schedule_item.html', {'item': item})


@login_required(login_url='planner:login')
def delete_schedule_item(request, item_id):
    """Delete a schedule item"""
    item = get_object_or_404(ScheduleItem, id=item_id, schedule__user=request.user)
    schedule_id = item.schedule.id
    item.delete()
    return redirect("planner:schedule_view", schedule_id)


@login_required(login_url='planner:login')
def toggle_schedule_item(request, item_id):
    """Toggle schedule item completion"""
    item = get_object_or_404(ScheduleItem, id=item_id, schedule__user=request.user)
    if item.status == 'completed':
        item.status = 'not_started'
    else:
        item.status = 'completed'
    item.save()  # save() will auto-sync is_done from status
    return redirect("planner:schedule_view", item.schedule.id)


@login_required(login_url='planner:login')
def delete_schedule(request, schedule_id):
    """Delete a schedule"""
    schedule = Schedule.objects.filter(id=schedule_id, user=request.user).first()
    if not schedule:
        messages.error(request, "This schedule does not exist or was already deleted.")
        return redirect('planner:schedule_home')

    if request.method == "POST":
        schedule.delete()
        messages.success(request, "Schedule deleted successfully.")
        return redirect('planner:schedule_home')

    return render(request, 'confirm_delete.html', {
        'object': schedule,
        'type': 'schedule'
    })


@login_required(login_url='planner:login')
def export_schedule_pdf(request, schedule_id):
    """Export schedule as PDF"""
    schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)
    items = schedule.items.all().order_by("id")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{schedule.name}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Schedule: {schedule.name}")

    y = height - 100
    p.setFont("Helvetica", 12)
    for item in items:
        status = "[x]" if item.is_done else "[ ]"
        p.drawString(60, y, f"{status} {item.title}")
        y -= 20
        if y < 50:
            p.showPage()
            y = height - 50

    p.showPage()
    p.save()
    return response