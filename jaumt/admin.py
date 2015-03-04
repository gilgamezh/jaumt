from django.contrib import admin

# Register your models here.
from jaumt.models import Url, Website


admin.site.register(Website)
admin.site.register(Url)


