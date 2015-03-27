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

import logging

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django_fsm import FSMIntegerField, transition
from django.conf import settings

logger = logging.getLogger(__name__)


class RecipientList(models.Model):
    description = models.CharField(
        max_length=300, help_text=_("Human readable description for a recipient list"))
    recipients = models.ManyToManyField(
        User, help_text=_("A list of Jaumt users that are member of this list"))

    def __str__(self):
        return self.description


class Website(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=140,)
    enabled = models.BooleanField(default=False, blank=True)
    owner = models.ForeignKey(User)
    recipients_list = models.ManyToManyField(
        RecipientList, help_text=_("A list of users that will receive alerts and notifications "
                                   " for this website")
    )

    def __str__(self):
        return self.name


class UrlStatusEnum():
    DOWNTIME = 10
    RETRYING = 20
    WARNING = 30
    OK = 40


class Url(models.Model):
    """ An Url to check """
    description = models.CharField(
        max_length=255, help_text=_(""" Details about the URL that Jaumt will check. This
                                    description will be used to identify the URL on all the
                                    alerts and metrics.
                                    e.g.: 'Gilgamezh's blog home'
                                    'Gilgamezh's blog. webserver1'  """))
    website = models.ForeignKey(Website, related_name='urls')
    url = models.URLField(help_text=_("Url to check"))
    hostname = models.CharField(
        max_length=255, null=True, blank=True, help_text=_("Host header for the request"))
    check_ssl = models.BooleanField(
        default=False, help_text=_("If enabled ssl cert will be checked"))
    timeout = models.IntegerField(default=30, help_text=_("Request timeout in seconds"))
    response_ms_sla = models.IntegerField(
        default=200, help_text=_("Expected response in milliseconds A.K.A. SLA"))
    check_interval = models.IntegerField(
        default=120, help_text=_("Default interval's check in seconds"))
    no_cache = models.BooleanField(
        default=False, blank=True, help_text=_(""" If you check this option a query string argument
                                               named 'jaumt' with a random string will be passed
                                               to the url.\n
                                               e.g.: example.com?jaumt=nbvli959NoLXKFGuCj40 """))
    match_text = models.CharField(
        max_length=500, null=True, blank=True, help_text=_(
            "This text have to exist in de response content."))
    no_match_text = models.CharField(
        max_length=500, null=True, blank=True, help_text=_("The opposite to match_text"))
    recipients_list = models.ManyToManyField(
        RecipientList, blank=True, null=True, help_text=_(""" By default the website recipient list
                                                          will be used. If you select at least one
                                                          here the default will be overwritten"""))
    alert_footer = models.TextField(blank=True, help_text=_(
        "This text will be attached on the alert message. Use it to link your documentation ;)."))
    enabled = models.BooleanField(default=False, blank=True)
    # not editables
    status = FSMIntegerField(default=UrlStatusEnum.OK, protected=True, editable=False)
    current_status_code = models.CharField(max_length=300, null=True, editable=False)
    modified = models.DateTimeField(null=True, editable=False, auto_now=True)
    last_check = models.DateTimeField(editable=False, auto_now_add=True)
    next_check = models.DateTimeField(editable=False, auto_now_add=True)
    last_check_ok = models.DateTimeField('Last OK', null=True, editable=False)
    last_check_warn = models.DateTimeField('Last WARNING', null=True, editable=False)
    last_check_downtime = models.DateTimeField('Last DOWNTIME', null=True, editable=False)
    last_check_retrying = models.DateTimeField('Last RETRYING', null=True, editable=False)

    def __str__(self):
        return self.url

    def send_alerts(self):
        """ Send alerts for an Url """
        from_email = settings.JAUMT_EMAIL_FROM
        if self.status == UrlStatusEnum.WARNING:
            current_status = 'ERROR'
        else:
            current_status = 'OK'
        subject = '{}[{}] {}'.format(settings.JAUMT_EMAIL_PREFIX, current_status, self.description)
        message = ("""Current status for {} is: {} \n\r
                   Url: {} \n\r
                   Current http_status or error message: {} \n\r
                   Last Check: {} \n\r
                   Last Check OK: {} \n\r
                   Url comments: \n\r
                   {}""").format(self.description, current_status, self.url,
                                 self.current_status_code, self.last_check, self.last_check_ok,
                                 self.alert_footer)
        recipient_lists = []
        if len(self.recipients_list.all()) > 0:
            # if url has a recipient_list use it
            recipients = self.recipients_list
        else:
            # else use the website recipient_list as default
            recipients = self.website.recipients_list

        for recipient in recipients.all():
            for user in recipient.recipients.all():
                recipient_lists.append(user.email)
        # Deleting duplicateds
        recipient_lists = list(set(recipient_lists))
        from jaumt.tasks import send_email_alert  # NOQA
        send_email_alert.delay(subject, message, from_email, recipient_lists)

    def check_url(self):
        """ Call the task to check an Url. """
        from jaumt.tasks import http_get  # NOQA
        http_get.delay(self.pk)

    @transition(field=status, source=[UrlStatusEnum.WARNING, UrlStatusEnum.RETRYING],
                target=UrlStatusEnum.OK)
    def set_ok(self, send_alerts=False):
        """ Transition to set the OK status and trigger all the related stuff to it """
        self.last_check_ok = timezone.now()
        self.next_check = (timezone.now() + timezone.timedelta(seconds=self.check_interval))
        if send_alerts:
            self.send_alerts()
            logger.info("Sending OK alerts for %s", self.url)
        logger.info("%s current status: OK . Next Check: %s", self.url, self.next_check)

    @transition(field=status, source=UrlStatusEnum.OK, target=UrlStatusEnum.WARNING)
    def set_warning(self):
        """ Transition to set the WARNING  status and trigger all the related stuff to it """
        self.last_check_warn = timezone.now()
        self.next_check = (
            timezone.now() + timezone.timedelta(seconds=self.check_interval / 4))
        logger.info("%s current status: WARNING . Next Check: %s", self.url, self.next_check)

    @transition(field=status, source=[UrlStatusEnum.RETRYING, UrlStatusEnum.WARNING],
                target=UrlStatusEnum.DOWNTIME)
    def set_downtime(self, send_alerts=False):
        """ Transition to set the DOWNTIME  status and trigger all the related stuff to it """
        self.last_check_error = timezone.now()
        self.next_check = (timezone.now() + timezone.timedelta(seconds=self.check_interval / 2))
        if send_alerts:
            self.send_alerts()
            logger.info("Sending DOWNTIME alerts for %s.", self.url)
        logger.info("%s current status: DOWNTIME . Next Check: %s", self.url, self.next_check)

    @transition(field=status, source=UrlStatusEnum.DOWNTIME, target=UrlStatusEnum.RETRYING)
    def set_retrying(self):
        """ Transition to set the RETRYING  status and trigger all the related stuff to it """
        self.last_check_retrying = timezone.now()
        self.next_check = (timezone.now() + timezone.timedelta(seconds=self.check_interval / 4))
        logger.info("%s current status: RETRYING. Next Check: %s", self.url, self.next_check)

    def handle_response(self, response=None, is_error=False, error_msg=None):
        """ Receive a response object and decide if it is an error or not. """
        logger.debug("Handling response is_error: %s error_msg: %s response: %s",
                     is_error, error_msg, response)
        self.last_check = timezone.now()
        if not is_error:
            if response.ok:
                if (self.match_text != '' and self.match_text not in response.text):
                    current_status_code = 'match_text not found'
                    is_error = True
                elif (self.no_match_text != '' and self.no_match_text in response.text):
                    current_status_code = 'no_match_text found'
                    is_error = True
                else:
                    current_status_code = '{}'.format(response.status_code)
                    is_error = False

            else:
                current_status_code = '{}'.format(response.status_code)
                is_error = True
        else:
            current_status_code = 'Error: {}'.format(error_msg)
            is_error = True

        self.update_status(is_error, current_status_code)

    def update_status(self, is_error=False, current_status_code=None):
        """ Update the Url status according to the current status"""
        logger.debug("Updating status: is_error: %s, current_status_code: %s",
                     is_error, current_status_code)
        self.current_status_code = current_status_code
        if not is_error:
            if self.status == UrlStatusEnum.OK:
                self.next_check = (
                    timezone.now() + timezone.timedelta(seconds=self.check_interval))
                logger.info("%s current status: OK. Next Check: %s", self.url, self.next_check)
            elif self.status == UrlStatusEnum.WARNING:
                self.set_ok()
            elif self.status == UrlStatusEnum.RETRYING:
                self.set_ok(send_alerts=True)
            elif self.status == UrlStatusEnum.DOWNTIME:
                self.set_retrying()
        else:
            if self.status == UrlStatusEnum.DOWNTIME:
                self.next_check = (
                    timezone.now() + timezone.timedelta(seconds=self.check_interval / 2))
                logger.info(
                    "%s current status: DOWNTIME. Next Check: %s", self.url, self.next_check)
            elif self.status == UrlStatusEnum.OK:
                self.set_warning()
            elif self.status == UrlStatusEnum.WARNING:
                self.set_downtime(send_alerts=True)
            elif self.status == UrlStatusEnum.RETRYING:
                self.set_downtime()
        self.save()
        # send to graphite status_code, response_time, size, etc
        # push_metrics.delay()
