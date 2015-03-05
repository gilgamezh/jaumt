from django.contrib import admin

# Register your models here.
from jaumt.models import Url, Website, RecipientList


class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'enabled', 'owner')
    list_filter = ['owner']


class UrlAdmin(admin.ModelAdmin):
    list_display = ('website', 'description', 'url', 'current_status',
                    'enabled', 'last_check')
    list_filter = ['website', 'current_status']

admin.site.register(Website, WebsiteAdmin)
admin.site.register(Url, UrlAdmin)
admin.site.register(RecipientList)


