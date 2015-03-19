from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View

from jaumt.models import Url

# Create your views here.
class MyView(View):
    def get(self, requests):
        urls = ' \n'.join([url.description for url in Url.objects.all()])
        return HttpResponse(urls)
