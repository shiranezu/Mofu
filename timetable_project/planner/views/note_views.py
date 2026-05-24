from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ..models import Note, StudyCategory


@login_required(login_url='planner:login')
def notes_home(request):
    notes = Note.objects.filter(user=request.user)
    categories = StudyCategory.objects.filter(user=request.user)
    return render(request, 'notes_home.html', {'notes': notes, 'categories': categories})


@login_required(login_url='planner:login')
def create_note(request):
    note = Note.objects.create(user=request.user, title='Untitled', content='')
    return redirect('planner:note_detail', note_id=note.id)


@login_required(login_url='planner:login')
def note_detail(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    categories = StudyCategory.objects.filter(user=request.user)
    return render(request, 'note_editor.html', {'note': note, 'categories': categories})


@login_required(login_url='planner:login')
@require_POST
def save_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.title = request.POST.get('title', 'Untitled').strip() or 'Untitled'
    note.content = request.POST.get('content', '')
    cat_id = request.POST.get('category')
    note.category = StudyCategory.objects.filter(id=cat_id, user=request.user).first() if cat_id else None
    note.save()
    return JsonResponse({
        'status': 'ok',
        'title': note.title,
        'updated_at': note.updated_at.strftime('%b %d, %Y · %I:%M %p'),
        'category_color': note.category.color if note.category else '#6B7FD4',
        'category_name': note.category.name if note.category else '',
    })


@login_required(login_url='planner:login')
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    if request.method == 'POST':
        note.delete()
        return redirect('planner:notes_home')
    return render(request, 'confirm_delete.html', {'object': note, 'type': 'note'})