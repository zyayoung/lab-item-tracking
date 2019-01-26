from django.shortcuts import render, redirect
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
from inventory.models import LocationPermissionApplication, Location, Item
from trace_item.models import ItemLog
from login.models import User


ban_list = ['app_list', 'calender']


def show_urls(url_list, depth=0):
    ret = {}
    for entry in url_list:
        if type(entry) == django.urls.resolvers.URLPattern:
            if str(entry.pattern) and str(entry.pattern)[0] == r'^' and entry.name and entry.name not in ban_list:
                ret.update({str(entry.name): str(entry.pattern)})
        if hasattr(entry, 'url_patterns'):
            if entry.app_name in ['inventory', 'login', 'trace_item', 'personal', 'traffic']:
                ret.update(show_urls(entry.url_patterns, depth + 1))
    return ret


def wash_regex(r):
    return re.sub(r'\?P<.+?>', '', r)


def check_admin(func):
    def inner(*args, **kwargs):
        request = args[1]
        if not request.session.get('is_superadmin', False):
            return redirect('inventory:index')
        return func(*args, **kwargs)
    return inner


class Pages(generic.View):
    @check_admin
    def get(self, requset):
        urlpatterns = show_urls(urls.urlpatterns)
        page_traffic = []
        avgt = {}
        maxt = {}
        totalTime = {}
        totalTimes = {}
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
                avgt.update({name: round(avg_time)})
                maxt.update({name: round(max_time)})
                totalTime.update({name: round(tot_time)})
                totalTimes.update({name: count})

        return render(requset, 'traffic/pages.html', locals())


class Calender(generic.View):
    @check_admin
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


class Users(generic.View):
    @check_admin
    def get(self, request):
        start = datetime.date.today()
        end = start + datetime.timedelta(days=1)
        user_data = [{
            'name': 'Other',
            'value': Traffic.objects.filter(datetime__range=(start, end), user=None).count(),
        }]
        for user in User.objects.all():
            count = Traffic.objects.filter(datetime__range=(start, end), user=user).count()
            if count:
                user_data.append({
                    'name': user.name,
                    'value': count
                })
        relation_nodes = []
        relation_links = []
        for user in User.objects.all():
            if not user.is_superadmin:
                relation_nodes.append({
                    'name': user.name,
                    'category': 1 if user.permission_str() == "员工" else 0,
                    'sc': user.staff.count()
                })
                for staff in user.staff.all():
                    relation_links.append({
                        'source': user.name,
                        'target': staff.name,
                    })
        return render(request, 'traffic/users.html', locals())


class Locations(generic.View):
    @check_admin
    def get(self, request):
        start = datetime.date.today()
        end = start + datetime.timedelta(days=1)
        loc_data = []
        relation_nodes = []
        relation_links = []
        locmap = {}
        revlocmap = []
        max_depth = 0
        tot_cnt = 0
        for idx, loc in enumerate(Location.objects.all()):
            count = ItemLog.objects.filter(time__range=(start, end), location_from=loc).count() + \
                    ItemLog.objects.filter(time__range=(start, end), location_to=loc).count()
            if count:
                loc_data.append({
                    'name': loc.__str__(),
                    'value': count,
                })
            depth = loc.__str__().count('-')
            max_depth = max(max_depth, depth)
            count = Item.objects.filter(location=loc).count()
            relation_nodes.append({
                'name': loc.path,
                'category': depth,
                'id': idx,
                'symbolSize': count,
                'value': count,
            })
            tot_cnt += count
            locmap[loc.__str__()] = idx
            revlocmap.append(loc.__str__())  # fast bls
        for idx, loc in enumerate(Location.objects.all()):
            if loc.parent:
                relation_links.append({
                    # 'source': locmap[loc.parent.__str__()],
                    # 'target': locmap[loc.__str__()],
                    'source': locmap[loc.parent.__str__()],
                    'target': locmap[loc.__str__()],
                })
        categories = [{'name':  i} for i in range(max_depth)]

        # Accumulate size
        for depth in range(max_depth - 1):
            selected_depth = max_depth - depth - 1
            for idx, loc in enumerate(relation_nodes):
                if loc['category'] == selected_depth:
                    parent_ida = locmap['-'.join(revlocmap[idx].split('-')[:-1])]
                    relation_nodes[parent_ida]['symbolSize'] += loc['symbolSize']

        # normalize
        for i in range(len(relation_nodes)):
            relation_nodes[i]['symbolSize'] = int(relation_nodes[i]['symbolSize'] / tot_cnt * 100) + 10
        return render(request, 'traffic/locations.html', locals())
