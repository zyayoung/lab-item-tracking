from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from lab_item_tracking import urls
import django.urls.resolvers


def show_urls(urllist, depth=0):
    ret = {}
    for entry in urllist:
        if type(entry) == django.urls.resolvers.URLPattern:
            ret.update({entry.pattern: entry.name})
        if hasattr(entry, 'url_patterns'):
            ret.update(show_urls(entry.url_patterns, depth + 1))
    return ret


class Pages(generic.View):
    def get(self, requset):
        return HttpResponse(show_urls(urls.urlpatterns))
