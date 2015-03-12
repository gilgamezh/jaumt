import requests

from celery import shared_task
from django.core.mail import send_mail

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



# Ejecutar tareas en grupo
# from jaumt.models import Url
# from celery import group
# from jaumt.tasks import check_url
# g = group([check_url.s(url.pk) for url in Url.objects.all()])
# g.apply_async()
