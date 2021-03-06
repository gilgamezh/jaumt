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
import requests_mock
from unittest.mock import MagicMock

from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings

from jaumt.models import Url, UrlStatusEnum, Website, RecipientList
from jaumt.tasks import send_email_alert


class UrlTestCase(TestCase):
    """ Tests for the Url model. """
    # users
    def setUp(self):
        self.monesvol = User.objects.create_user('monesvol', email='monesvol@jaumt.com')
        self.pirate = User.objects.create_user('pirate', email='pirate@jaumt.com')
        self.gilgamezh = User.objects.create_user('gilgamezh', email='gilgamezh@jaumt.com')
        # recipient lists
        self.recipient_list1 = RecipientList.objects.create(description='test recipient list 1')
        self.recipient_list1.recipients.add(self.monesvol)
        self.recipient_list1.recipients.add(self.pirate)
        self.recipient_list2 = RecipientList.objects.create(description='test recipient list 2')
        self.recipient_list2.recipients.add(self.pirate)
        self.recipient_list2.recipients.add(self.gilgamezh)
        # websites
        self.test_site1 = Website.objects.create(name='testsite', description='test site',
                                                 owner=self.gilgamezh)
        self.test_site1.recipients_list.add(self.recipient_list1)
        self.test_site2 = Website.objects.create(name='testsite2', description='test site 2',
                                                 owner=self.pirate)
        self.test_site2.recipients_list.add(self.recipient_list2)
        #  settings
        settings.JAUMT_EMAIL_FROM = 'jaumt@jaumt.com'
        settings.JAUMT_EMAIL_PREFIX = '[Jaumt]'
        settings.JAUMT_USER_AGENT = "User-Agent': 'Jaumt/0.1 (+http://jaumt.com)"

    #  Url.update_status() tests
    def test_url_status_ok_error(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 status=UrlStatusEnum.OK,
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=True, current_status_code='404')
        self.assertFalse(url.send_alerts.called)
        self.assertEqual(url.status, UrlStatusEnum.WARNING)

    def test_url_status_ok_ok(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 status=UrlStatusEnum.OK,
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=False, current_status_code='200')
        self.assertFalse(url.send_alerts.called)
        self.assertEqual(url.status, UrlStatusEnum.OK)

    def test_url_status_warning_error(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 status=UrlStatusEnum.WARNING,
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=True, current_status_code='500')
        self.assertTrue(url.send_alerts.called)
        self.assertEqual(url.status, UrlStatusEnum.DOWNTIME)

    def test_url_status_warning_ok(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 status=UrlStatusEnum.WARNING,
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=False, current_status_code='200')
        self.assertFalse(url.send_alerts.called)
        self.assertEqual(url.status, UrlStatusEnum.OK)

    def test_url_status_downtime_error(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 status=UrlStatusEnum.DOWNTIME,
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=True, current_status_code='500')
        self.assertFalse(url.send_alerts.called)
        self.assertEqual(url.status, UrlStatusEnum.DOWNTIME)

    def test_url_status_downtime_ok(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 status=UrlStatusEnum.DOWNTIME,
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=False, current_status_code='200')
        self.assertFalse(url.send_alerts.called)
        self.assertEqual(url.status, UrlStatusEnum.RETRYING)

    def test_url_status_retrying_error(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 status=UrlStatusEnum.RETRYING,
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=True, current_status_code='500')
        self.assertFalse(url.send_alerts.called)
        self.assertEqual(url.status, UrlStatusEnum.DOWNTIME)

    def test_url_status_retrying_ok(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 status=UrlStatusEnum.RETRYING,
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=False, current_status_code='200')
        self.assertTrue(url.send_alerts.called)
        self.assertEqual(url.status, UrlStatusEnum.OK)

    #  Url.handle_response() tests
    def test_url_handle_response_with_error(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 enabled=True)
        url.update_status = MagicMock()
        url.handle_response(is_error=True, error_msg='Foo bar')
        url.update_status.assert_called_with(True, 'Error: Foo bar')

    def test_url_handle_response_ok(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 match_text='',
                                 no_match_text='',
                                 enabled=True)
        adapter = requests_mock.Adapter()
        session = requests.Session()
        session.mount('mock', adapter)
        adapter.register_uri('GET', 'mock://jaumt.com', text='foo bar')
        response = session.get('mock://jaumt.com')
        url.update_status = MagicMock()
        url.handle_response(response=response)
        url.update_status.assert_called_with(False, '200')

    def test_url_handle_response_error(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 match_text='',
                                 no_match_text='',
                                 enabled=True)
        adapter = requests_mock.Adapter()
        session = requests.Session()
        session.mount('mock', adapter)
        adapter.register_uri('GET', 'mock://jaumt.com', text='foo bar', status_code=500)
        response = session.get('mock://jaumt.com')
        url.update_status = MagicMock()
        url.handle_response(response=response)
        url.update_status.assert_called_with(True, '500')

    def test_url_handle_response_match_text_ok(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 match_text='foo',
                                 no_match_text='',
                                 enabled=True)
        adapter = requests_mock.Adapter()
        session = requests.Session()
        session.mount('mock', adapter)
        adapter.register_uri('GET', 'mock://jaumt.com', text='foo bar', status_code=200)
        response = session.get('mock://jaumt.com')
        url.update_status = MagicMock()
        url.handle_response(response=response)
        url.update_status.assert_called_with(False, '200')

    def test_url_handle_response_match_text_error(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 match_text='foo',
                                 no_match_text='',
                                 enabled=True)
        adapter = requests_mock.Adapter()
        session = requests.Session()
        session.mount('mock', adapter)
        adapter.register_uri('GET', 'mock://jaumt.com', text='bar', status_code=200)
        response = session.get('mock://jaumt.com')
        url.update_status = MagicMock()
        url.handle_response(response=response)
        url.update_status.assert_called_with(True, 'match_text not found')

    def test_url_handle_response_no_match_text_error(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 match_text='',
                                 no_match_text='foo',
                                 enabled=True)
        adapter = requests_mock.Adapter()
        session = requests.Session()
        session.mount('mock', adapter)
        adapter.register_uri('GET', 'mock://jaumt.com', text='foo bar', status_code=200)
        response = session.get('mock://jaumt.com')
        url.update_status = MagicMock()
        url.handle_response(response=response)
        url.update_status.assert_called_with(True, 'no_match_text found')

    def test_url_handle_response_no_match_text_ok(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 match_text='',
                                 no_match_text='foo',
                                 enabled=True)
        adapter = requests_mock.Adapter()
        session = requests.Session()
        session.mount('mock', adapter)
        adapter.register_uri('GET', 'mock://jaumt.com', text='bar', status_code=200)
        response = session.get('mock://jaumt.com')
        url.update_status = MagicMock()
        url.handle_response(response=response)
        url.update_status.assert_called_with(False, '200')

    # test send_alerts()
    def test_send_ok_alert(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 status=UrlStatusEnum.RETRYING,
                                 match_text='',
                                 no_match_text='',
                                 current_status_code='TestCase',
                                 alert_footer='foo bar',
                                 enabled=True)
        send_email_alert.delay = MagicMock()
        url.last_check = '1982-08-02 11:11:11.000000+00:00'
        url.last_check_ok = '1982-08-02 11:11:11.000000+00:00'
        url.send_alerts()
        subject = '[Jaumt][OK] test site 1'
        message = ("""Current status for test site 1 is: OK \n\r
                   Url: http://example.com \n\r
                   Current http_status or error message: TestCase \n\r
                   Last Check: 1982-08-02 11:11:11.000000+00:00 \n\r
                   Last Check OK: 1982-08-02 11:11:11.000000+00:00 \n\r
                   Url comments: \n\r
                   foo bar""")
        from_email = 'jaumt@jaumt.com'
        recipient_lists = ['pirate@jaumt.com', 'monesvol@jaumt.com']
        call_args = send_email_alert.delay.call_args[0]
        self.assertEqual(call_args[0], subject)
        self.assertEqual(call_args[1], message)
        self.assertEqual(call_args[2], from_email)
        self.assertCountEqual(call_args[3], recipient_lists)

    def test_send_error_alert(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 status=UrlStatusEnum.WARNING,
                                 match_text='',
                                 no_match_text='',
                                 current_status_code='TestCase',
                                 alert_footer='foo bar',
                                 enabled=True)
        send_email_alert.delay = MagicMock()
        url.last_check = '1982-08-02 11:11:11.000000+00:00'
        url.last_check_ok = '1982-08-02 11:11:11.000000+00:00'
        url.send_alerts()
        subject = '[Jaumt][ERROR] test site 1'
        message = ("""Current status for test site 1 is: ERROR \n\r
                   Url: http://example.com \n\r
                   Current http_status or error message: TestCase \n\r
                   Last Check: 1982-08-02 11:11:11.000000+00:00 \n\r
                   Last Check OK: 1982-08-02 11:11:11.000000+00:00 \n\r
                   Url comments: \n\r
                   foo bar""")
        from_email = 'jaumt@jaumt.com'
        recipient_lists = ['pirate@jaumt.com', 'monesvol@jaumt.com']
        call_args = send_email_alert.delay.call_args[0]
        self.assertEqual(call_args[0], subject)
        self.assertEqual(call_args[1], message)
        self.assertEqual(call_args[2], from_email)
        self.assertCountEqual(call_args[3], recipient_lists)

    def test_send_ok_alert_with_url_rcps(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 status=UrlStatusEnum.RETRYING,
                                 match_text='',
                                 no_match_text='',
                                 current_status_code='TestCase',
                                 alert_footer='foo bar',
                                 enabled=True)
        url.recipients_list.add(self.recipient_list2)
        url.last_check = '1982-08-02 11:11:11.000000+00:00'
        url.last_check_ok = '1982-08-02 11:11:11.000000+00:00'
        url.save()
        send_email_alert.delay = MagicMock()
        url.send_alerts()
        subject = '[Jaumt][OK] test site 1'
        message = ("""Current status for test site 1 is: OK \n\r
                   Url: http://example.com \n\r
                   Current http_status or error message: TestCase \n\r
                   Last Check: 1982-08-02 11:11:11.000000+00:00 \n\r
                   Last Check OK: 1982-08-02 11:11:11.000000+00:00 \n\r
                   Url comments: \n\r
                   foo bar""")
        from_email = 'jaumt@jaumt.com'
        recipient_lists = ['pirate@jaumt.com', 'gilgamezh@jaumt.com']
        call_args = send_email_alert.delay.call_args[0]
        self.assertEqual(call_args[0], subject)
        self.assertEqual(call_args[1], message)
        self.assertEqual(call_args[2], from_email)
        self.assertCountEqual(call_args[3], recipient_lists)

    def test_send_ok_alert_with_two_url_rcps(self):
        url = Url.objects.create(description='test site 1',
                                 website=self.test_site1,
                                 url='http://example.com',
                                 status=UrlStatusEnum.RETRYING,
                                 match_text='',
                                 no_match_text='',
                                 current_status_code='TestCase',
                                 alert_footer='foo bar',
                                 enabled=True)
        url.recipients_list.add(self.recipient_list2)
        url.recipients_list.add(self.recipient_list1)
        url.last_check = '1982-08-02 11:11:11.000000+00:00'
        url.last_check_ok = '1982-08-02 11:11:11.000000+00:00'
        url.save()
        send_email_alert.delay = MagicMock()
        url.send_alerts()
        subject = '[Jaumt][OK] test site 1'
        message = ("""Current status for test site 1 is: OK \n\r
                   Url: http://example.com \n\r
                   Current http_status or error message: TestCase \n\r
                   Last Check: 1982-08-02 11:11:11.000000+00:00 \n\r
                   Last Check OK: 1982-08-02 11:11:11.000000+00:00 \n\r
                   Url comments: \n\r
                   foo bar""")
        from_email = 'jaumt@jaumt.com'
        recipient_lists = ['pirate@jaumt.com', 'gilgamezh@jaumt.com', 'monesvol@jaumt.com']
        call_args = send_email_alert.delay.call_args[0]
        self.assertEqual(call_args[0], subject)
        self.assertEqual(call_args[1], message)
        self.assertEqual(call_args[2], from_email)
        self.assertCountEqual(call_args[3], recipient_lists)
