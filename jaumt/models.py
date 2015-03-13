from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django_fsm import FSMField, transition


class RecipientList(models.Model):
    description = models.CharField(max_length=300)
    recipients = models.ManyToManyField(User)

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
    hostname = models.CharField(max_length=500, null=True, blank=True)
    timeout = models.IntegerField(default=2000)
    response_ms_sla = models.IntegerField(default=200)
    check_interval = models.IntegerField(default=60)
    no_cache = models.BooleanField(default=False, blank=True)
    match_text = models.CharField(max_length=100, null=True, blank=True)
    no_match_text = models.CharField(max_length=100, null=True, blank=True)
    recipients_list = models.ManyToManyField(RecipientList,
                                             blank=True,
                                             null=True)
    alert_footer = models.CharField(max_length=500, blank=True)
    enabled = models.BooleanField(default=False, blank=True)
    # not editables
    status = FSMField(default='OK', protected=True, editable=False)
    current_status_code = models.CharField(max_length=300, null=True,
                                           editable=False)
    modified = models.DateTimeField(null=True, editable=False, auto_now=True)
    last_check = models.DateTimeField(editable=False, auto_now_add=True)
    next_check = models.DateTimeField(editable=False, auto_now_add=True)
    last_check_ok = models.DateTimeField('Last OK',
                                         null=True, editable=False)
    last_check_warn = models.DateTimeField('Last WARNING',
                                           null=True, editable=False)
    last_check_downtime = models.DateTimeField('Last DOWNTIME',
                                               null=True, editable=False)
    last_check_retrying = models.DateTimeField('Last RETRYING',
                                               null=True, editable=False)

    def __str__(self):
        return "{} - Last Check {} - {}. ".format(self.url, self.last_check,
                                                  self.status)

    def send_alerts(self):
        subject = '[{}] {}'.format(self.status, self.description)
        message = "HTTP Status code: {} \n {}".format(
            self.current_status_code, self.alert_footer)
        from_email = 'soporte@cmd.com.ar'
        # FIXME Poner esto como una config general
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
        from jaumt.tasks import send_email_alert
        send_email_alert.delay(subject, message, from_email, recipient_lists)

    def check_url(self):
        """ Call http_get task and sets handle_status as callback. """
        from jaumt.tasks import http_get
        http_get.delay(self.pk)

    @transition(field=status, source=['WARNING', 'RETRYING'], target='OK')
    def set_ok(self, send_alerts=False):
        self.last_check_ok = timezone.now()
        self.next_check = (
            timezone.now() + timezone.timedelta(seconds=self.check_interval))
        if send_alerts:
            self.send_alerts()

    @transition(field=status, source='OK', target='WARNING')
    def set_warning(self):
        self.last_check_warn = timezone.now()
        self.next_check = (
            timezone.now() + timezone.timedelta(
                seconds=self.check_interval / 4))

    @transition(field=status, source=['RETRYING', 'WARNING'],
                target='DOWNTIME')
    def set_downtime(self, send_alerts=True):
        self.last_check_error = timezone.now()
        self.next_check = (
            timezone.now() + timezone.timedelta(
                seconds=self.check_interval / 2))
        if send_alerts:
            self.send_alerts()

    @transition(field=status, source='DOWNTIME', target='RETRYING')
    def set_retrying(self):
        self.last_check_retrying = timezone.now()
        self.next_check = (
            timezone.now() + timezone.timedelta(
                seconds=self.check_interval / 4))

    def handle_response(self, response=None, is_error=False, error_msg=None):
        self.last_check = timezone.now()
        if not is_error:
            if response.ok:
                if (self.match_text != '' and
                    self.match_text not in response.text):
                    current_status_code = 'match_text not found'
                    is_error = True
                elif (self.no_match_text != '' and
                      self.no_match_text in response.text):
                    current_status_code = 'no_match_text found'
                    is_error = True
                else:
                    current_status_code = '{}'.format(response.status_code)
                    is_error = False

            else:
                current_status_code = '{}'.format(
                    response.status_code)
                is_error = True
        else:
            current_status_code = 'Exception: {}'.format(error_msg)
            is_error = True

        self.update_status(is_error, current_status_code)

    def update_status(self, is_error=False, current_status_code=None):
        self.current_status_code = current_status_code
        if not is_error:
            if self.status == 'OK':
                self.next_check = (
                    timezone.now() + timezone.timedelta(
                        seconds=self.check_interval))
            elif self.status == "WARNING":
                self.set_ok()
            elif self.status == "RETRYING":
                self.set_ok(send_alerts=True)
            elif self.status == "DOWNTIME":
                self.set_retrying()
        else:
            if self.status == 'DOWNTIME':
                self.next_check = (timezone.now() + timezone.timedelta(
                    seconds=self.check_interval / 2))
            elif self.status == "OK":
                self.set_warning()
            elif self.status == "WARNING":
                self.set_downtime(send_alerts=True)
            elif self.status == "RETRYING":
                self.set_downtime()
        self.save()
        # send to graphite status_code, response_time, size, etc
        # push_metrics.delay()
