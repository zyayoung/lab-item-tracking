from django.shortcuts import render
from django.views import generic

from trace_item.models import ItemLog
from inventory.utils import get_my_item, get_my_loc
from login.models import User as myUser


class TraceItemView(generic.View):
    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        item = get_my_item(tmp_user, kwargs.get('id'))
        logs = ItemLog.objects.filter(item=item)
        return render(request, 'trace_item/trace_item.html', locals())


class TraceLocationView(generic.View):
    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        loc = get_my_loc(tmp_user, kwargs.get('id'))
        logs = ItemLog.objects.filter(location_to=loc) | ItemLog.objects.filter(location_from=loc)
        return render(request, 'trace_item/trace_location.html', locals())
