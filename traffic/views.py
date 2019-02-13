from django.shortcuts import render
from django.views import generic
from lab_item_tracking import urls
from django.db.models import Count, Min, Max, Sum, Avg
import datetime
import numpy as np
from .utils import *
from traffic.models import *
from inventory.models import LocationPermissionApplication, Location, Item
from login.models import User
from log.models import Log
from django.views.decorators.cache import cache_page
from django.utils.translation import gettext_lazy as _


@check_admin
@cache_page(60 * 15)
def page_view(requset):
    urlpatterns = show_urls(urls.urlpatterns)
    page_traffic = []
    avgt = {}
    maxt = {}
    totalTime = {}
    totalTimes = {}
    traffic = Traffic.objects.filter(
        id__gt=Traffic.objects.count() - int(requset.GET.get('count', 2500)))
    for name in urlpatterns.keys():
        r = wash_regex(urlpatterns[name].replace('^', '^/'))
        objects = traffic.filter(url__regex=r)
        count = objects.count()
        if count > 0:
            tot_time = objects.aggregate(
                Sum('response_time'))['response_time__sum']
            avg_time = objects.aggregate(
                Avg('response_time'))['response_time__avg']
            max_time = objects.aggregate(
                Max('response_time'))['response_time__max']
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


@check_admin
@cache_page(60 * 15)
def calender_view(request):
    traffic_data = []
    locreq_data = []
    itemlog_data = []
    traffic_num = []
    traffic_label = []
    locreq_num = []
    itemlog_num = []
    CalenderCache.objects.filter(need_update=True).delete()
    for i in range(365, -1, -1):
        start = datetime.date.today() - datetime.timedelta(days=i)
        end = start + datetime.timedelta(days=1)
        if not CalenderCache.objects.filter(
                date_str=start.strftime("%Y-%m-%d")).exists():
            new_cache = CalenderCache.objects.create(
                date_str=start.strftime("%Y-%m-%d"),
                traffic_cnt=Traffic.objects.filter(
                    datetime__range=(start, end)).count(),
                locreq_cnt=LocationPermissionApplication.objects.filter(
                    time__range=(start, end)).count(),
                itemlog_cnt=Log.objects.filter(time__range=(start,
                                                            end)).count(),
                need_update=start.strftime("%Y-%m-%d") == datetime.date.
                today().strftime("%Y-%m-%d"))
            new_cache.save()
        cache = CalenderCache.objects.get(date_str=start.strftime("%Y-%m-%d"))
        traffic_data.append([
            start.strftime("%Y-%m-%d"),
            cache.traffic_cnt,
        ])
        traffic_label.append(start.strftime("%Y-%m-%d"))
        locreq_data.append([
            start.strftime("%Y-%m-%d"),
            cache.locreq_cnt,
        ])
        itemlog_data.append([
            start.strftime("%Y-%m-%d"),
            cache.itemlog_cnt,
        ])
        traffic_num.append(traffic_data[-1][1])
        locreq_num.append(locreq_data[-1][1])
        itemlog_num.append(itemlog_data[-1][1])
    traffic_max = np.percentile(np.array(traffic_num), 100)
    locreq_max = np.percentile(np.array(locreq_num), 100)
    itemlog_max = np.percentile(np.array(itemlog_num), 100)
    date_range = [itemlog_data[0][0], itemlog_data[-1][0]]
    return render(request, 'traffic/calendar.html', locals())


@check_admin
@cache_page(60 * 15)
def users_view(request):
    try:
        bias = min(0, int(request.GET.get('bias', 0)))
    except ValueError:
        bias = 0
    start = datetime.date.today() + datetime.timedelta(days=bias)
    end = start + datetime.timedelta(days=1)
    user_data = [{
        'name':
        'Other',
        'value':
        Traffic.objects.filter(datetime__range=(start, end),
                               user=None).count(),
    }]
    series_hour_data = []
    for hour in range(25):
        d = datetime.datetime(start.year, start.month,
                              start.day) + datetime.timedelta(hours=hour)
        series_hour_data.append(
            Traffic.objects.filter(
                datetime__range=(d, d + datetime.timedelta(hours=1)),
                user=None,
            ).count())
    series_hour = [{
        'name': 'Other',
        'type': 'line',
        'areaStyle': {},
        'stack': _('总量'),
        'data': series_hour_data
    }]
    legend = ['Other']
    xAxis = list(range(24))
    for user in User.objects.all():
        count = Traffic.objects.filter(
            datetime__range=(start, end), user=user).count()
        if count:
            user_data.append({'name': user.name, 'value': count})
            series_hour_data = []
            for hour in range(24):
                d = datetime.datetime(
                    start.year, start.month,
                    start.day) + datetime.timedelta(hours=hour)
                series_hour_data.append(
                    Traffic.objects.filter(
                        datetime__range=(d, d + datetime.timedelta(hours=1)),
                        user=user,
                    ).count())
            legend.append(user.name)
            series_hour.append({
                'name': user.name,
                'type': 'line',
                'areaStyle': {},
                'stack': _('总量'),
                'data': series_hour_data
            })
    relation_nodes = []
    relation_links = []
    for user in User.objects.all():
        if not user.is_superadmin:
            relation_nodes.append({
                'name':
                user.name,
                'category':
                1 if user.permission_str() == _("员工") else 0,
                'sc':
                user.staff.count()
            })
            for staff in user.staff.all():
                relation_links.append({
                    'source': user.name,
                    'target': staff.name,
                })
    return render(request, 'traffic/users.html', locals())


@check_admin
@cache_page(60 * 15)
def locations_view(request):
    start = datetime.date.today()
    end = start + datetime.timedelta(days=1)
    loc_data = []
    for idx, loc in enumerate(Location.objects.all()):
        count = Log.objects.filter(
            time__range=(start, end), category='位置', before=loc.id).count()
        count += Log.objects.filter(
            time__range=(start, end), category='位置', after=loc.id).count()
        if count:
            loc_data.append({
                'name': loc.__str__(),
                'value': count,
            })
    loc_node, item_count = build_loc_tree(count=True, link=True)
    loc_data_children = loc_node['children']
    return render(request, 'traffic/locations.html', locals())
