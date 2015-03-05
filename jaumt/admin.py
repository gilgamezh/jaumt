from django.contrib import admin

# Register your models here.
from jaumt.models import Url, Website, RecipientList


admin.site.register(Website)
admin.site.register(Url)
admin.site.register(RecipientList)


