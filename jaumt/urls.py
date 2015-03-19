from django.conf.urls import patterns, include, url
from django.contrib import admin
from jaumt.views import MyView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'jaumt.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^jaumt/', MyView.as_view()),
)
