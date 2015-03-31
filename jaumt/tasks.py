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

from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils.crypto import get_random_string


from jaumt.models import Url

logger = logging.getLogger(__name__)

LOCK_EXPIRE = 60 * 5  # Lock expires in 5 minutes


@shared_task
def http_get(url_pk):
    """ Celery task to check a Url. """
    url = Url.objects.get(pk=url_pk)
    payload = None
    if url.no_cache:
        no_cache_string = get_random_string(length=42)
        payload = {'jaumt': no_cache_string}
    headers = {'User-Agent': settings.JAUMT_USER_AGENT}
    if url.hostname != '':
        headers['Host'] = url.hostname
    if url.check_ssl:
        verify = True
    else:
        verify = False
    try:
        logger.info("Checking %s, No Cache: %s Headers: %s Timeout: %s",
                    url.url, url.no_cache, headers, url.timeout)
        response = requests.get(url.url, params=payload, headers=headers, timeout=url.timeout,
                                verify=verify)
        logger.debug("Response: Headers: %s HTTP_status_code: %s",
                     response.headers, response.status_code)
        url.handle_response(response)
    except requests.exceptions.RequestException as error:
        url.handle_response(response=None, is_error=True, error_msg=str(error))
        logger.error('Request to %s failed with error: %s', url.url, error)
    finally:
        lock_id = 'lock-{}'.format(url.pk)
        cache.delete(lock_id)


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
    urls = Url.objects.filter(
        next_check__lte=timezone.now()).exclude(enabled=False).exclude(website__enabled=False)
    for url in urls:

        lock_id = 'lock-{}'.format(url.pk)

        def acquire_lock():
            return cache.add(lock_id, url.url, LOCK_EXPIRE)

        def release_lock():
            return cache.delete(lock_id)

        if acquire_lock():
            logger.info("Queuing %s::%s to check", url.description, url.url)
            try:
                url.check_url()
            except:
                release_lock()
        else:
            logger.debug('Url %s::%s is already being checked by another worker', url.description,
                         url.url)
