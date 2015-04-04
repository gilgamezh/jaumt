# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipientList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('description', models.CharField(help_text='Human readable description for a recipient list', max_length=300)),
                ('recipients', models.ManyToManyField(to=settings.AUTH_USER_MODEL, help_text='A list of Jaumt users that are member of this list')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Url',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('description', models.CharField(help_text=" Details about the URL that Jaumt will check. This\n                                    description will be used to identify the URL on all the\n                                    alerts and metrics.\n                                    e.g.: 'Gilgamezh's blog home'\n                                    'Gilgamezh's blog. webserver1'  ", max_length=255)),
                ('url', models.URLField(help_text='Url to check')),
                ('hostname', models.CharField(null=True, blank=True, help_text='Host header for the request', max_length=255)),
                ('check_ssl', models.BooleanField(help_text='If enabled ssl cert will be checked', default=False)),
                ('timeout', models.IntegerField(help_text='Request timeout in seconds', default=30)),
                ('response_ms_sla', models.IntegerField(help_text='Expected response in milliseconds A.K.A. SLA', default=200)),
                ('check_interval', models.IntegerField(help_text="Default interval's check in seconds", default=120)),
                ('no_cache', models.BooleanField(help_text=" If you check this option a query string argument\n                                               named 'jaumt' with a random string will be passed\n                                               to the url.\n\n                                               e.g.: example.com?jaumt=nbvli959NoLXKFGuCj40 ", default=False)),
                ('match_text', models.CharField(null=True, blank=True, help_text='This text have to exist in de response content.', max_length=500)),
                ('no_match_text', models.CharField(null=True, blank=True, help_text='The opposite to match_text', max_length=500)),
                ('alert_footer', models.TextField(blank=True, help_text='This text will be attached on the alert message. Use it to link your documentation ;).')),
                ('enabled', models.BooleanField(default=False)),
                ('status', django_fsm.FSMIntegerField(protected=True, editable=False, default=40, choices=[(40, 'OK'), (30, 'WARNING'), (10, 'DOWNTIME'), (20, 'RETRYING')])),
                ('current_status_code', models.CharField(null=True, editable=False, max_length=300)),
                ('modified', models.DateTimeField(null=True, auto_now=True)),
                ('last_check', models.DateTimeField(auto_now_add=True)),
                ('next_check', models.DateTimeField(auto_now_add=True)),
                ('last_check_ok', models.DateTimeField(null=True, editable=False, verbose_name='Last OK')),
                ('last_check_warn', models.DateTimeField(null=True, editable=False, verbose_name='Last WARNING')),
                ('last_check_downtime', models.DateTimeField(null=True, editable=False, verbose_name='Last DOWNTIME')),
                ('last_check_retrying', models.DateTimeField(null=True, editable=False, verbose_name='Last RETRYING')),
                ('recipients_list', models.ManyToManyField(null=True, to='jaumt.RecipientList', blank=True, help_text=' By default the website recipient list\n                                                          will be used. If you select at least one\n                                                          here the default will be overwritten')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('description', models.CharField(max_length=140)),
                ('enabled', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('recipients_list', models.ManyToManyField(to='jaumt.RecipientList', help_text='A list of users that will receive alerts and notifications  for this website')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='url',
            name='website',
            field=models.ForeignKey(to='jaumt.Website', related_name='urls'),
            preserve_default=True,
        ),
    ]
