import requests

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string

from jaumt.models import Url


@shared_task
def http_get(url_pk):
    url = Url.objects.get(pk=url_pk)
    payload = None
    if url.no_cache:
        no_cache_string = get_random_string(length=42)
        payload = {'jaumt': no_cache_string}
    # FIXME poner user-agent en una config
    headers = {'User-Agent': 'Jaumt/0.1 (+http://jaumt.example.com)'}
    if url.hostname != '':
        headers['Host'] = url.hostname
    try:
        response = requests.get(url.url, params=payload, headers=headers,
                                timeout=url.timeout)
        url.handle_response(response)
    except requests.exceptions.RequestException as error:
        url.handle_response(response=None, is_error=True,
                            error_msg=str(error))


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
    urls = Url.objects.filter(next_check__lte=timezone.now())
    urls = urls.exclude(enabled=False)
    for url in urls:
        url.check_url()

