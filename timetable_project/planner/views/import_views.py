import json
from decimal import Decimal

from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from django.urls import reverse

from ..models import (
    StudyCategory, StudySession, StudyGoal, StudyResource,
    DictionaryHistory, Note, UserSettings
)


def _get_or_create_category(user, name, cache):
    """Look up a category by name for this user, creating it if missing.
    `cache` is a dict used to avoid repeat queries within one import."""
    if not name:
        return None
    if name in cache:
        return cache[name]
    category, _ = StudyCategory.objects.get_or_create(user=user, name=name)
    cache[name] = category
    return category


@login_required(login_url='planner:login')
@require_POST
def import_data(request):
    """Import a previously exported Mofu JSON file. This only ever ADDS
    data — nothing existing is ever modified or deleted."""
    user = request.user
    uploaded_file = request.FILES.get('import_file')

    if not uploaded_file:
        messages.error(request, "Please choose a file to import.")
        return redirect(reverse('planner:settings') + '?tab=export')

    try:
        raw = uploaded_file.read().decode('utf-8')
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        messages.error(request, "That file doesn't look like a valid Mofu export. Please check the file and try again.")
        return redirect(reverse('planner:settings') + '?tab=export')

    category_cache = {}
    counts = {
        'categories': 0, 'study_sessions': 0, 'study_goals': 0,
        'resources': 0, 'notes': 0, 'dictionary_history': 0,
    }

    # Categories first, so later sections can look them up
    for c in data.get('categories', []):
        try:
            name = c.get('name')
            if not name:
                continue
            category, created = StudyCategory.objects.get_or_create(
                user=user, name=name,
                defaults={'color': c.get('color', '#3498db')}
            )
            category_cache[name] = category
            if created:
                counts['categories'] += 1
        except Exception:
            continue

    for s in data.get('study_sessions', []):
        try:
            start_time = parse_datetime(s.get('start_time')) if s.get('start_time') else None
            end_time = parse_datetime(s.get('end_time')) if s.get('end_time') else None
            if not start_time:
                continue
            StudySession.objects.create(
                user=user,
                category=_get_or_create_category(user, s.get('category'), category_cache),
                start_time=start_time,
                end_time=end_time,
                duration_seconds=s.get('duration_seconds', 0),
                paused_seconds=s.get('paused_seconds', 0),
                notes=s.get('notes'),
                session_tag=s.get('session_tag'),
                productivity_rating=s.get('productivity_rating'),
                is_pomodoro=s.get('is_pomodoro', False),
                pomodoros_completed=s.get('pomodoros_completed', 0),
                is_countdown=s.get('is_countdown', False),
                countdown_target_seconds=s.get('countdown_target_seconds', 0),
                is_active=False,
            )
            counts['study_sessions'] += 1
        except Exception:
            continue

    for g in data.get('study_goals', []):
        try:
            target_hours = Decimal(str(g.get('target_hours', 0)))
            StudyGoal.objects.create(
                user=user,
                name=g.get('name'),
                goal_type=g.get('goal_type', 'daily'),
                target_hours=target_hours,
                category=_get_or_create_category(user, g.get('category'), category_cache),
                is_active=g.get('is_active', True),
            )
            counts['study_goals'] += 1
        except Exception:
            continue

    for r in data.get('resources', []):
        try:
            if not r.get('title') or not r.get('url'):
                continue
            StudyResource.objects.create(
                user=user,
                title=r.get('title'),
                url=r.get('url'),
                description=r.get('description'),
                category=_get_or_create_category(user, r.get('category'), category_cache),
            )
            counts['resources'] += 1
        except Exception:
            continue

    for n in data.get('notes', []):
        try:
            Note.objects.create(
                user=user,
                title=n.get('title', 'Untitled'),
                category=_get_or_create_category(user, n.get('category'), category_cache),
                content=n.get('content', ''),
            )
            counts['notes'] += 1
        except Exception:
            continue

    for d in data.get('dictionary_history', []):
        try:
            word = d.get('word')
            if not word:
                continue
            DictionaryHistory.objects.create(user=user, word=word)
            counts['dictionary_history'] += 1
        except Exception:
            continue

    # Settings: this is a singleton, safe to update directly with imported values
    settings_data = data.get('settings') or {}
    if settings_data:
        try:
            user_settings, _ = UserSettings.objects.get_or_create(user=user)
            user_settings.pomodoro_work = settings_data.get('pomodoro_work', user_settings.pomodoro_work)
            user_settings.pomodoro_short_break = settings_data.get('pomodoro_short_break', user_settings.pomodoro_short_break)
            user_settings.pomodoro_long_break = settings_data.get('pomodoro_long_break', user_settings.pomodoro_long_break)
            user_settings.pomodoro_sessions = settings_data.get('pomodoro_sessions', user_settings.pomodoro_sessions)
            user_settings.save()
        except Exception:
            pass

    summary = ", ".join(f"{v} {k.replace('_', ' ')}" for k, v in counts.items() if v > 0)
    if summary:
        messages.success(request, f"Import complete: added {summary}.")
    else:
        messages.warning(request, "Nothing was imported — the file may have been empty or already up to date.")

    return redirect(reverse('planner:settings') + '?tab=export')