from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='planner:login')
def home(request):
    """Homepage"""
    return render(request, 'select_timetable.html')


@login_required(login_url='planner:login')
def help(request):
    """Help page"""
    return render(request, 'help.html')

