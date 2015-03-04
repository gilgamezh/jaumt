from django.db import models


class URL(models.Models):
    OK = 0
    WARNING = 1
    ERROR = 2

    STATUS_CHOICES = (
        (OK, 'Ok'),
        (WARNING, 'Warning'),
        (ERROR, 'Error')
    )

    description = models.CharField(max_length=140)
    url = models.URLField()
    hostname = models.URLField()
    timeout = models.IntegerField(default=2000)
    no_cache = models.BooleanField()
    response_ms_sla = models.IntegerField(default=200)
    match_text = models.CharField(max_length=100)
    no_match_text = models.CharField(max_length=100)
    enabled = models.BooleanField()
    current_status = models.IntegerField(choices=STATUS_CHOICES,
                                         default=OK)
    last_check_ok = models.DateTimeField('Last OK')
    last_check_warn = models.DateTimeField('Last WARNING')
    last_check_error = models.DateTimeField('Last ERROR')


class Website(models.Models):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=140)
    url = models.ForeignKey(URL)
    enabled = models.BooleanField()

    def __str__(self):
        return self.name


