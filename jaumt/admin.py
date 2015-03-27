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

from jaumt.models import Url, Website, RecipientList


def make_enable(modeladmin, request, queryset):
    queryset.update(enabled=True)
make_enable.short_description = "Mark selected items as enabled"


def make_disable(modeladmin, request, queryset):
    queryset.update(enabled=False)
make_disable.short_description = "Mark selected items as disabled"


class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'enabled', 'owner')
    list_filter = ['owner']
    actions = [make_enable, make_disable]


class UrlAdmin(admin.ModelAdmin):
    list_display = ('website', 'description', 'url', 'status', 'current_status_code', 'enabled',
                    'last_check', 'next_check')
    list_filter = ['website', 'status']
    actions = [make_enable, make_disable]

admin.site.register(Website, WebsiteAdmin)
admin.site.register(Url, UrlAdmin)
admin.site.register(RecipientList)
