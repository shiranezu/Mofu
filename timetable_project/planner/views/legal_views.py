from django.shortcuts import render


def privacy_policy(request):
    """Standalone privacy policy page - no login required."""
    return render(request, 'privacy.html')


def terms_of_use(request):
    """Standalone terms of use page - no login required."""
    return render(request, 'terms.html')