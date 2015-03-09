from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Group, User
from django_fsm import FSMField, transition

from jaumt.tasks import http_get


class RecipientList(models.Model):
    description = models.CharField(max_length=300)
    recipients = models.ManyToManyField(Group)

    def __str__(self):
        return self.description


class Website(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=140)
    enabled = models.BooleanField(default=False, blank=True)
    owner = models.ForeignKey(User)
    recipients_list = models.ManyToManyField(RecipientList)

    def __str__(self):
        return self.name


class Url(models.Model):
    """ Url Object """
    description = models.CharField(max_length=140)
    website = models.ForeignKey(Website, related_name='urls')
    url = models.URLField()
    hostname = models.URLField(null=True, blank=True)
    timeout = models.IntegerField(default=2000)
    response_ms_sla = models.IntegerField(default=200)
    no_cache = models.BooleanField(default=False, blank=True)
    match_text = models.CharField(max_length=100, null=True, blank=True)
    no_match_text = models.CharField(max_length=100, null=True, blank=True)
    recipients_list = models.ManyToManyField(RecipientList,
                                             blank=True,
                                             null=True)
    enabled = models.BooleanField(default=False, blank=True)
    # not editables
    status = FSMField(default='OK', protected=True)
    current_status_hits = models.IntegerField(default=0)
    current_status_code = models.IntegerField(null=True, editable=False)
    modified = models.DateTimeField(null=True, editable=False, auto_now=True)
    last_check = models.DateTimeField(null=True, editable=False)
    last_check_ok = models.DateTimeField('Last OK',
                                         null=True,
                                         editable=False)
    last_check_warn = models.DateTimeField('Last WARNING',
                                           null=True,
                                           editable=False)
    last_check_error = models.DateTimeField('Last ERROR',
                                            null=True,
                                            editable=False)

    def __str__(self):
        return "{} - Last Check {} - {}. ".format(self.url, self.last_check,
                                                  self.status)

    def check_url(self):
        """ Call http_get task and sets handle_status as callback. """
        http_get.apply_async((self.id), link=self.handle_status())

    @transition(field=status, source='WARNING', target='OK')
    def set_ok(self):
        self.last_check_ok = timezone.now()
        #send_email_alert.delay() OK

    @transition(field=status, source=['ERROR', 'OK'], target='WARNING')
    def set_warning(self):
        self.last_check_warn = timezone.now()

    @transition(field=status, source='WARNING', target='ERROR')
    def set_error(self):
        self.last_check_error = timezone.now()
        #send_email_alert.delay() ERROR

    def handle_status(self, response):
        self.current_status_code = response.status_code
        self.last_check = timezone.now()
        if response.ok:
            if self.status == self.WARNING:
                self.set_ok()
            elif self.status == self.ERROR:
                self.set_warning()
        else:
            if self.status == self.OK:
                self.set_warning()

            elif self.status == self.WARNING:
                self.set_error()

        # send to graphite status_code, response_time, size, etc
        #push_metrics.delay()
