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
from django.views.generic.list import ListView
from django.utils import timezone
from django.conf import settings

from jaumt.models import Url, UrlStatusEnum


# Create your views here.
class Home(View):
    def get(self, requests):
        return render(requests, 'jaumt/home.html')


class StatusUrl(View):
    def get(self, requests, url_id):
        url = Url.objects.get(pk=url_id)
        context = {'url': url, 'UrlStatusEnum': UrlStatusEnum}
        return render(requests, 'jaumt/status_url.html', context)


class UrlListView(ListView):
    model = Url
    paginate_by = settings.PAGINATE_SIZE
    context_object_name = 'urls'
    template_name = 'jaumt/status.html'

    def get_queryset(self):
        order_by = self.request.GET.get('order_by', default='status')
        filter_by_status = self.request.GET.getlist('status',
                                                    default=[UrlStatusEnum.WARNING,
                                                             UrlStatusEnum.DOWNTIME,
                                                             UrlStatusEnum.RETRYING])
        queryset = Url.objects.all().order_by(order_by).exclude(
            enabled=False).exclude(website__enabled=False)
        queryset = queryset.filter(status__in=filter_by_status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(UrlListView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['UrlStatusEnum'] = UrlStatusEnum
        return context

