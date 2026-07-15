"""
URL configuration for timetable_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin, messages
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.core.cache import cache
from django.shortcuts import redirect
 
 
class RateLimitedPasswordResetView(auth_views.PasswordResetView):
    template_name = 'auth/password_reset.html'
    email_template_name = 'auth/password_reset_email.txt'
 
    RESET_LIMIT = 3
    RESET_WINDOW = 3600  # 1 hour
 
    def post(self, request, *args, **kwargs):
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        cache_key = f'password_reset_attempts_{ip}'
        attempts = cache.get(cache_key, 0)
 
        if attempts >= self.RESET_LIMIT:
            messages.error(request, 'Too many reset requests. Please try again in an hour.')
            return redirect('password_reset')
 
        cache.set(cache_key, attempts + 1, timeout=self.RESET_WINDOW)
        return super().post(request, *args, **kwargs)
 



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('planner.urls', namespace='planner')),

     # Password reset

    path('password-reset/', RateLimitedPasswordResetView.as_view(), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html',
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html',
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html',
    ), name='password_reset_complete'),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)