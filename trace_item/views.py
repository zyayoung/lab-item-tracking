from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from inventory.models import Item, Location
from trace_item.models import ItemLog
from inventory.utils import get_my_item, get_my_loc, get_my_list
from login.models import User as myUser


class TraceItemView(generic.View):
    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        item = get_my_item(tmp_user, kwargs.get('id'))
        logs = ItemLog.objects.filter(item=item)
        my_list = get_my_list(tmp_user, Location.objects.all())
        logs = logs.filter(location_from__in=my_list, location_to=None) |\
            logs.filter(location_from__in=my_list, location_to__in=my_list) |\
            logs.filter(location_from=None, location_to__in=my_list) |\
            logs.filter(location_from=None, location_to=None)
        return render(request, 'trace_item/trace_item.html', locals())


class TraceLocationView(generic.View):
    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        loc = get_my_loc(tmp_user, kwargs.get('id'))
        logs = ItemLog.objects.filter(location_to=loc) | ItemLog.objects.filter(location_from=loc)
        my_list = get_my_list(tmp_user, Item.objects.filter(is_property=False))
        logs = logs.filter(item__in=my_list)
        return render(request, 'trace_item/trace_location.html', locals())


class TraceUserView(generic.View):
    def get(self, request, *args, **kwargs):
        user = get_object_or_404(myUser, id=kwargs.get('id'))
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        logs = ItemLog.objects.filter(operator=user)
        my_list = get_my_list(tmp_user, Item.objects.filter(is_property=False))
        logs = logs.filter(item__in=my_list)
        my_list = get_my_list(tmp_user, Location.objects.all())
        logs = logs.filter(location_from__in=my_list, location_to=None) |\
            logs.filter(location_from__in=my_list, location_to__in=my_list) |\
            logs.filter(location_from=None, location_to__in=my_list) |\
            logs.filter(location_from=None, location_to=None)
        return render(request, 'trace_item/trace_user.html', locals())
