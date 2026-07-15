from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from ..forms import RegistrationForm

# Simple in-memory/cache-based rate limiting — no extra package required.
# Limits are per IP address.
LOGIN_LIMIT = 5          # attempts
LOGIN_WINDOW = 300        # seconds (5 minutes)
REGISTER_LIMIT = 3
REGISTER_WINDOW = 3600    # 1 hour


def _is_rate_limited(request, key_prefix, limit, window_seconds):
    """Returns True if this IP has exceeded `limit` attempts within
    `window_seconds`. Tracks attempts using Django's cache framework."""
    ip = request.META.get('REMOTE_ADDR', 'unknown')
    cache_key = f'{key_prefix}_{ip}'
    attempts = cache.get(cache_key, 0)

    if attempts >= limit:
        return True

    cache.set(cache_key, attempts + 1, timeout=window_seconds)
    return False


def login_user(request):
    if request.method == 'POST':
        if _is_rate_limited(request, 'login_attempts', LOGIN_LIMIT, LOGIN_WINDOW):
            messages.error(request, 'Too many login attempts. Please wait a few minutes and try again.')
            return render(request, 'auth/login.html')

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
            # Successful login clears the rate-limit counter for this IP
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            cache.delete(f'login_attempts_{ip}')
            return redirect('planner:home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'auth/login.html')


def register(request):
    form = RegistrationForm()
    if request.method == 'POST':
        if _is_rate_limited(request, 'register_attempts', REGISTER_LIMIT, REGISTER_WINDOW):
            messages.error(request, 'Too many sign-up attempts from this device. Please try again later.')
            return render(request, 'auth/register.html', {'form': form})

        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Send welcome email
            from django.core.mail import send_mail
            from django.template.loader import render_to_string

            email_body = render_to_string('auth/welcome_email.txt', {'user': user})
            send_mail(
                subject='Welcome to Mofu!',
                message=email_body,
                from_email=None,  # uses DEFAULT_FROM_EMAIL
                recipient_list=[user.email],
                fail_silently=True,
            )

            login(request, user)
            return redirect('planner:home')
    return render(request, 'auth/register.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('planner:login')