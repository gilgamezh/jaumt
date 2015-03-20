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

from django.contrib import admin
# from fsm_admin.mixins import FSMTransitionMixin

from jaumt.models import Url, Website, RecipientList


class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'enabled', 'owner')
    list_filter = ['owner']


# class UrlAdmin(FSMTransitionMixin, admin.ModelAdmin):
class UrlAdmin(admin.ModelAdmin):
    list_display = ('website', 'description', 'url', 'status', 'current_status_code', 'enabled',
                    'last_check', 'next_check')
    list_filter = ['website', 'status']
    # fsm_field = ['status',]

admin.site.register(Website, WebsiteAdmin)
admin.site.register(Url, UrlAdmin)
admin.site.register(RecipientList)
