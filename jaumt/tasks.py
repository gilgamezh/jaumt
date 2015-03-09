import requests

from celery import shared_task


@shared_task
def http_get(url):
    response = requests.get(url)
    return response


@shared_task
def push_metrics(name, value, timestamp=None):
    pass


@shared_task
def send_email_alert(recipients, alert):
    pass


# Ejecutar tareas en grupo
# from jaumt.models import Url
# from celery import group
# from jaumt.tasks import check_url
# g = group([check_url.s(url.pk) for url in Url.objects.all()])
# g.apply_async()
