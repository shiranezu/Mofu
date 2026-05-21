from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from ..models import TaskBoard, Task
from ..forms import TaskBoardForm, TaskForm


@login_required(login_url='planner:login')
def tasks_home(request):
    task_boards = TaskBoard.objects.filter(user=request.user)
    boards_data = []
    for tb in task_boards:
        total = tb.tasks.count()
        completed = tb.tasks.filter(status='completed').count()
        pending = total - completed
        percentage = int((completed / total * 100)) if total > 0 else 0
        boards_data.append({
            'task_board': tb,
            'total': total,
            'completed': completed,
            'pending': pending,
            'percentage': percentage,
        })
    return render(request, 'tasks_home.html', {
        'boards_data': boards_data,
        'task_boards': task_boards,
    })


@login_required(login_url='planner:login')
def task_board(request, board_id):
    tb = get_object_or_404(TaskBoard, id=board_id, user=request.user)
    tasks = tb.tasks.all().order_by("due_date", "id")
    today = timezone.now().date()
    return render(request, "task_board.html", {
        "task_board": tb,
        "tasks": tasks,
        "today": today,
    })


@login_required(login_url='planner:login')
def quick_add_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        priority = request.POST.get('priority', 'medium')
        due_date = request.POST.get('due_date')
        tb, _ = TaskBoard.objects.get_or_create(user=request.user, name="Quick Tasks")
        Task.objects.create(
            task_board=tb,
            title=title,
            priority=priority,
            due_date=due_date if due_date else None,
            status='not_started'
        )
        messages.success(request, f"Task '{title}' added!")
    return redirect('planner:home')


@login_required(login_url='planner:login')
def create_task_board(request):
    form = TaskBoardForm(request.POST or None)
    if form.is_valid():
        tb = form.save(commit=False)
        tb.user = request.user
        tb.save()
        return redirect("planner:task_board", tb.id)
    return render(request, "add_generic.html", {"form": form, "title": "Create Task Board"})


@login_required(login_url='planner:login')
def add_task(request, board_id):
    tb = get_object_or_404(TaskBoard, id=board_id, user=request.user)
    form = TaskForm(request.POST or None)
    if form.is_valid():
        task = form.save(commit=False)
        task.task_board = tb
        task.save()
        return redirect("planner:task_board", tb.id)
    return render(request, "add_generic.html", {"form": form, "title": "Add Task"})


@login_required(login_url='planner:login')
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, task_board__user=request.user)
    form = TaskForm(request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        return redirect("planner:task_board", task.task_board.id)
    return render(request, "add_generic.html", {"form": form, "title": "Edit Task"})


@login_required(login_url='planner:login')
def view_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, task_board__user=request.user)
    return render(request, 'view_task.html', {
        'item': task,
        'today': timezone.now().date(),
    })


@login_required(login_url='planner:login')
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, task_board__user=request.user)
    board_id = task.task_board.id
    task.delete()
    return redirect("planner:task_board", board_id)


@login_required(login_url='planner:login')
def toggle_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, task_board__user=request.user)
    task.status = 'not_started' if task.status == 'completed' else 'completed'
    task.save()
    return redirect("planner:task_board", task.task_board.id)


@login_required(login_url='planner:login')
def delete_task_board(request, board_id):
    tb = TaskBoard.objects.filter(id=board_id, user=request.user).first()
    if not tb:
        messages.error(request, "This task board does not exist or was already deleted.")
        return redirect('planner:tasks_home')
    if request.method == "POST":
        tb.delete()
        messages.success(request, "Task board deleted successfully.")
        return redirect('planner:tasks_home')
    return render(request, 'confirm_delete.html', {'object': tb, 'type': 'task board'})


@login_required(login_url='planner:login')
def export_tasks_pdf(request, board_id):
    tb = get_object_or_404(TaskBoard, id=board_id, user=request.user)
    tasks = tb.tasks.all().order_by("id")
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{tb.name}.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Tasks: {tb.name}")
    y = height - 100
    p.setFont("Helvetica", 12)
    for task in tasks:
        status = "[x]" if task.is_done else "[ ]"
        p.drawString(60, y, f"{status} {task.title}")
        y -= 20
        if y < 50:
            p.showPage()
            y = height - 50
    p.showPage()
    p.save()
    return response