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

from django.shortcuts import render
from django.views.generic import View

from jaumt.models import Url, UrlStatusEnum


# Create your views here.
class Status(View):
    def get(self, requests):
        urls = Url.objects.all().order_by('status').exclude(
            enabled=False).exclude(website__enabled=False)
        context = {'urls': urls, 'UrlStatusEnum': UrlStatusEnum}
        return render(requests, 'jaumt/status.html', context)


class Home(View):
    def get(self, requests):
        return render(requests, 'jaumt/home.html')


class StatusUrl(View):
    def get(self, requests, url_id):
        url = Url.objects.get(pk=url_id)
        context = {'url': url, 'UrlStatusEnum': UrlStatusEnum}
        return render(requests, 'jaumt/status_url.html', context)
