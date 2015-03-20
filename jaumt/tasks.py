# Copyright 2015 Nicolás Demarchi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General
# Public License version 3, as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#
# For further info, check  https://github.com/gilgamezh/jaumt

import requests
import logging

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string

from jaumt.models import Url

logger = logging.getLogger(__name__)


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
        logger.info("Checking %s, No Cache: %s Headers: %s Timeout: %s",
                    url.url, url.no_cache, headers, url.timeout)
        response = requests.get(url.url, params=payload, headers=headers, timeout=url.timeout)
        logger.debug("Response: Headers: %s HTTP_status_code: %s",
                     response.headers, response.status_code)
        url.handle_response(response)
    except requests.exceptions.RequestException as error:
        url.handle_response(response=None, is_error=True, error_msg=str(error))
        logger.error('Request to %s failed with error: %s', url.url, error)


@shared_task
def push_metrics(name, value, timestamp=None):
    pass


@shared_task
def send_email_alert(subject, message, from_email, recipient_list):
    """ Recibe una tupla (subject, message, from_email, recipient_list)
    y llama a send_mass_mail con la misma """
    logger.debug("Sending alert to %s with subject: %s", recipient_list, subject)
    send_mail(subject, message, from_email, recipient_list)


@shared_task
def queue_checks():
    urls = Url.objects.filter(next_check__lte=timezone.now())
    urls = urls.exclude(enabled=False)
    for url in urls:
        logger.info("Queuing %s to check", url.url)
        url.check_url()
