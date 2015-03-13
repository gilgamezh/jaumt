from django.contrib import admin
#from fsm_admin.mixins import FSMTransitionMixin

from jaumt.models import Url, Website, RecipientList


class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'enabled', 'owner')
    list_filter = ['owner']


#class UrlAdmin(FSMTransitionMixin, admin.ModelAdmin):
class UrlAdmin(admin.ModelAdmin):
    list_display = ('website', 'description', 'url', 'status',
                    'current_status_code', 'enabled', 'last_check',
                    'next_check')
    list_filter = ['website', 'status']
    #fsm_field = ['status',]

admin.site.register(Website, WebsiteAdmin)
admin.site.register(Url, UrlAdmin)
admin.site.register(RecipientList)


