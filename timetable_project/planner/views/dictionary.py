import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..models import DictionaryHistory

@login_required(login_url='planner:login')
def dictionary(request):
    """Look up word definitions"""
    word = request.GET.get('word', '').strip()
    definition_data = None
    error = None

    if word:
        try:
            response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')

            if response.status_code == 200:
                data = response.json()[0]
                meaning = data['meanings'][0]
                part_of_speech = meaning['partOfSpeech']
                definition = meaning['definitions'][0]['definition']
                example = meaning['definitions'][0].get('example', None)
                phonetic = data.get('phonetic', '')

                definition_data = {
                    'word': word,
                    'phonetic': phonetic,
                    'part_of_speech': part_of_speech,
                    'definition': definition,
                    'example': example,
                }

                # Save to history — avoid duplicates, keep only last 10
                DictionaryHistory.objects.filter(
                    user=request.user,
                    word__iexact=word
                ).delete()

                DictionaryHistory.objects.create(
                    user=request.user,
                    word=word
                )

                # Keep only last 10
                history = DictionaryHistory.objects.filter(user=request.user)
                if history.count() > 10:
                    oldest = history[10:]
                    DictionaryHistory.objects.filter(
                        id__in=[h.id for h in oldest]
                    ).delete()

            else:
                error = f"No definition found for '{word}'"
        except Exception:
            error = f"Error looking up '{word}'. Please try again."

    # Get recent history
    recent_words = DictionaryHistory.objects.filter(
        user=request.user
    ).exclude(word__iexact=word)[:10]

    return render(request, 'study/dictionary.html', {
        'definition_data': definition_data,
        'error': error,
        'search_word': word,
        'recent_words': recent_words,
    })


@login_required(login_url='planner:login')
def clear_dictionary_history(request):
    """Clear dictionary search history"""
    if request.method == 'POST':
        DictionaryHistory.objects.filter(user=request.user).delete()
    return redirect('planner:dictionary')