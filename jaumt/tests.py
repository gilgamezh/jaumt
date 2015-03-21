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

from django.test import TestCase
from unittest.mock import MagicMock

from jaumt.models import Url


class UrlTestCase(TestCase):
    """ Tests for the Url model. """

    #  Url.update_status() tests
    def test_url_status_ok_error(self):
        url = Url.objects.create(description='test site 1',
                                 website_id=1,
                                 url='http://example.com',
                                 status='OK',
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=True, current_status_code='404')
        self.assertFalse(url.send_alerts.called)
        self.assertEqual(url.status, 'WARNING')

    def test_url_status_ok_ok(self):
        url = Url.objects.create(description='test site 1',
                                 website_id=1,
                                 url='http://example.com',
                                 status='OK',
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=False, current_status_code='200')
        self.assertFalse(url.send_alerts.called)
        self.assertEqual(url.status, 'OK')

    def test_url_status_warning_error(self):
        url = Url.objects.create(description='test site 1',
                                 website_id=1,
                                 url='http://example.com',
                                 status='WARNING',
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=True, current_status_code='500')
        self.assertTrue(url.send_alerts.called)
        self.assertEqual(url.status, 'DOWNTIME')

    def test_url_status_warning_ok(self):
        url = Url.objects.create(description='test site 1',
                                 website_id=1,
                                 url='http://example.com',
                                 status='WARNING',
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=False, current_status_code='200')
        self.assertFalse(url.send_alerts.called)
        self.assertEqual(url.status, 'OK')

    def test_url_status_downtime_error(self):
        url = Url.objects.create(description='test site 1',
                                 website_id=1,
                                 url='http://example.com',
                                 status='DOWNTIME',
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=True, current_status_code='500')
        self.assertFalse(url.send_alerts.called)
        self.assertEqual(url.status, 'DOWNTIME')

    def test_url_status_downtime_ok(self):
        url = Url.objects.create(description='test site 1',
                                 website_id=1,
                                 url='http://example.com',
                                 status='DOWNTIME',
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=False, current_status_code='200')
        self.assertFalse(url.send_alerts.called)
        self.assertEqual(url.status, 'RETRYING')

    def test_url_status_retrying_error(self):
        url = Url.objects.create(description='test site 1',
                                 website_id=1,
                                 url='http://example.com',
                                 status='RETRYING',
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=True, current_status_code='500')
        self.assertFalse(url.send_alerts.called)
        self.assertEqual(url.status, 'DOWNTIME')

    def test_url_status_retrying_ok(self):
        url = Url.objects.create(description='test site 1',
                                 website_id=1,
                                 url='http://example.com',
                                 status='RETRYING',
                                 enabled=True)
        url.send_alerts = MagicMock()
        url.update_status(is_error=False, current_status_code='200')
        self.assertTrue(url.send_alerts.called)
        self.assertEqual(url.status, 'OK')

    #  Url.handle_response() tests
    def test_url_handle_response_with_error(self):
        url = Url.objects.create(description='test site 1',
                                 website_id=1,
                                 url='http://example.com',
                                 enabled=True)
        url.update_status = MagicMock()
        url.handle_response(is_error=True, error_msg='Foo bar')
        url.update_status.assert_called_with(True, 'Error: Foo bar')

    def test_url_handle_response_ok(self):
        url = Url.objects.create(description='test site 1',
                                 website_id=1,
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
                                 website_id=1,
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
                                 website_id=1,
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
                                 website_id=1,
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
                                 website_id=1,
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
                                 website_id=1,
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

