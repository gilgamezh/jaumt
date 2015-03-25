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

from django.conf.urls import patterns, include, url
from django.contrib import admin
from jaumt.views import Status, Home, StatusUrl

urlpatterns = patterns('',
                       # Examples:
                       url(r'^$', Home.as_view(), name='home'),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^status/', Status.as_view(), name='status'),
                       url(r'^url/(?P<url_id>\d+)/$', StatusUrl.as_view()),
                       )
