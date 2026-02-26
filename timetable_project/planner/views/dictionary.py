import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required(login_url='planner:login')
def dictionary(request):
    """Look up word definitions"""
    word = request.GET.get('word', '').strip()
    definition_data = None
    error = None
    
    if word:
        try:
            # Free Dictionary API
            response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
            
            if response.status_code == 200:
                data = response.json()[0]
                
                # Extract the first meaning
                meaning = data['meanings'][0]
                part_of_speech = meaning['partOfSpeech']
                definition = meaning['definitions'][0]['definition']
                example = meaning['definitions'][0].get('example', None)
                
                # Extract phonetic if available
                phonetic = data.get('phonetic', '')
                
                definition_data = {
                    'word': word,
                    'phonetic': phonetic,
                    'part_of_speech': part_of_speech,
                    'definition': definition,
                    'example': example,
                }
            else:
                error = f"No definition found for '{word}'"
        except Exception as e:
            error = f"Error looking up '{word}'. Please try again."
    
    return render(request, 'study/dictionary.html', {
        'definition_data': definition_data,
        'error': error,
        'search_word': word
    })