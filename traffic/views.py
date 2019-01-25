from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from lab_item_tracking import urls
import django.urls.resolvers
from django.db.models import Count, Min, Max, Sum, Avg
import re
import json

from traffic.models import Traffic


def show_urls(url_list, depth=0):
    ret = {}
    for entry in url_list:
        if type(entry) == django.urls.resolvers.URLPattern:
            if str(entry.pattern) and str(entry.pattern)[0] == r'^' and entry.name and entry.name != 'app_list':
                ret.update({str(entry.name): str(entry.pattern)})
        if hasattr(entry, 'url_patterns'):
            if entry.app_name in ['inventory', 'login', 'trace_item', 'personal', 'traffic']:
                ret.update(show_urls(entry.url_patterns, depth + 1))
    return ret


def wash_regex(r):
    return re.sub(r'\?P<.+?>', '', r)


class Pages(generic.View):
    def get(self, requset):
        urlpatterns = show_urls(urls.urlpatterns)
        page_traffic = []
        traffic = Traffic.objects.filter(user_id__gt=Traffic.objects.count()-10000)
        for name in urlpatterns.keys():
            r = wash_regex(urlpatterns[name].replace('^', '^/'))
            objects = traffic.filter(url__regex=r)
            count = objects.count()
            if count > 0:
                tot_time = objects.aggregate(Sum('response_time'))['response_time__sum']
                avg_time = objects.aggregate(Avg('response_time'))['response_time__avg']
                max_time = objects.aggregate(Max('response_time'))['response_time__max']
                page_traffic.append({
                    'name': name,
                    'url_pattern': urlpatterns[name],
                    'count': count,
                    'tot_time': float(tot_time),
                    'avg_time': float(avg_time),
                    'max_time': float(max_time)
                })
            else:
                page_traffic.append({
                    'name': name,
                    'url_pattern': urlpatterns[name],
                    'count': count,
                    'tot_time': 0,
                    'avg_time': 0,
                    'max_time': 0
                })
        return HttpResponse(json.dumps(page_traffic))
