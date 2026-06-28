from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone

from ..models import (
    StudyCategory, StudySession, StudyGoal, StudyResource,
    DictionaryHistory, Note, UserSettings
)


@login_required(login_url='planner:login')
def export_data(request):
    """Export all of a user's data (excluding Timetables, Tasks, and
    Schedule) as a downloadable JSON file."""
    user = request.user

    categories = StudyCategory.objects.filter(user=user)
    category_lookup = {c.id: c.name for c in categories}

    data = {
        'export_info': {
            'generated_at': timezone.now(),
            'app': 'Mofu',
        },
        'profile': {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'date_joined': user.date_joined,
        },
        'categories': [
            {
                'id': c.id,
                'name': c.name,
                'color': c.color,
            }
            for c in categories
        ],
        'study_sessions': [
            {
                'id': s.id,
                'category': category_lookup.get(s.category_id),
                'start_time': s.start_time,
                'end_time': s.end_time,
                'duration_seconds': s.duration_seconds,
                'paused_seconds': s.paused_seconds,
                'notes': s.notes,
                'session_tag': s.session_tag,
                'productivity_rating': s.productivity_rating,
                'is_pomodoro': s.is_pomodoro,
                'pomodoros_completed': s.pomodoros_completed,
                'is_countdown': s.is_countdown,
                'countdown_target_seconds': s.countdown_target_seconds,
                'created_at': s.created_at,
            }
            for s in StudySession.objects.filter(user=user, is_active=False)
        ],
        'study_goals': [
            {
                'id': g.id,
                'name': g.name,
                'goal_type': g.goal_type,
                'target_hours': g.target_hours,
                'category': category_lookup.get(g.category_id),
                'is_active': g.is_active,
                'created_at': g.created_at,
            }
            for g in StudyGoal.objects.filter(user=user)
        ],
        'resources': [
            {
                'id': r.id,
                'title': r.title,
                'url': r.url,
                'description': r.description,
                'category': category_lookup.get(r.category_id),
                'created_at': r.created_at,
            }
            for r in StudyResource.objects.filter(user=user)
        ],
        'notes': [
            {
                'id': n.id,
                'title': n.title,
                'category': category_lookup.get(n.category_id),
                'content': n.content,
                'created_at': n.created_at,
                'updated_at': n.updated_at,
            }
            for n in Note.objects.filter(user=user)
        ],
        'dictionary_history': [
            {
                'word': d.word,
                'searched_at': d.searched_at,
            }
            for d in DictionaryHistory.objects.filter(user=user)
        ],
        'settings': {},
    }

    try:
        settings_obj = UserSettings.objects.get(user=user)
        data['settings'] = {
            'pomodoro_work': settings_obj.pomodoro_work,
            'pomodoro_short_break': settings_obj.pomodoro_short_break,
            'pomodoro_long_break': settings_obj.pomodoro_long_break,
            'pomodoro_sessions': settings_obj.pomodoro_sessions,
        }
    except UserSettings.DoesNotExist:
        pass

    filename = f"mofu_export_{user.username}_{timezone.now().strftime('%Y-%m-%d')}.json"
    response = JsonResponse(data, encoder=DjangoJSONEncoder, json_dumps_params={'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response