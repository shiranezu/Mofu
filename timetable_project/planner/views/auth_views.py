from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from ..forms import RegistrationForm


def login_user(request):
    if request.method == 'POST':
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
            return redirect('planner:home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'auth/login.html')


def register(request):
    form = RegistrationForm
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('planner:home')
    return render(request, 'auth/register.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('planner:login')