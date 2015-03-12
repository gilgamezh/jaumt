import requests

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from jaumt.models import Url


@shared_task
def http_get(url_pk):
    url = Url.objects.get(pk=url_pk)
    response = requests.get(url.url)
    url.handle_status(response)


@shared_task
def push_metrics(name, value, timestamp=None):
    pass


@shared_task
def send_email_alert(subject, message, from_email, recipient_list):
    """ Recibe una tupla (subject, message, from_email, recipient_list)
    y llama a send_mass_mail con la misma """
    send_mail(subject, message, from_email, recipient_list)


@shared_task
def queue_checks():
    for url in Url.objects.filter(next_check__lte=timezone.now()):
        url.check_url()
