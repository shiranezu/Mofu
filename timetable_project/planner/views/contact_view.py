from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings as django_settings
from ..forms import ContactForm


def contact(request):
    """Standalone contact page - no login required."""
    sent = False

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            body = (
                f"New message from the Mofu contact page.\n\n"
                f"Name: {name}\n"
                f"Email: {email}\n\n"
                f"Message:\n{message}"
            )

            send_mail(
                subject=f"Mofu Contact: {name}",
                message=body,
                from_email=None,  # uses DEFAULT_FROM_EMAIL
                recipient_list=[django_settings.CONTACT_EMAIL],
                fail_silently=True,
            )
            sent = True
            form = ContactForm()  # reset after successful send
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form, 'sent': sent})