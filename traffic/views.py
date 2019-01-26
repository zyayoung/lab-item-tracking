from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from lab_item_tracking import urls
import django.urls.resolvers
from django.db.models import Count, Min, Max, Sum, Avg
import re
import json
import datetime
import numpy as np

from traffic.models import Traffic
from inventory.models import LocationPermissionApplication
from trace_item.models import ItemLog


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
        traffic = Traffic.objects.filter(id__gt=Traffic.objects.count()-5000)
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


class Calender(generic.View):
    def get(self, request):
        traffic_data = []
        locreq_data = []
        itemlog_data = []
        traffic_num = []
        locreq_num = []
        itemlog_num = []
        for i in range(365):
            start = datetime.date.today() - datetime.timedelta(days=i)
            end = start + datetime.timedelta(days=1)
            traffic_data.append([
                start.strftime("%Y-%m-%d"),
                Traffic.objects.filter(datetime__range=(start, end)).count()
            ])
            locreq_data.append([
                start.strftime("%Y-%m-%d"),
                LocationPermissionApplication.objects.filter(time__range=(start, end)).count()
            ])
            itemlog_data.append([
                start.strftime("%Y-%m-%d"),
                ItemLog.objects.filter(time__range=(start, end)).count()
            ])
            traffic_num.append(traffic_data[-1][1])
            locreq_num.append(locreq_data[-1][1])
            itemlog_num.append(itemlog_data[-1][1])
        traffic_max = np.percentile(np.array(traffic_num), 100)
        locreq_max = np.percentile(np.array(locreq_num), 100)
        itemlog_max = np.percentile(np.array(itemlog_num), 100)
        date_range = [traffic_data[0][0], traffic_data[-1][0]]
        return render(request, 'traffic/calendar.html', locals())
