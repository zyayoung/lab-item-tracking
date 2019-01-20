from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import (
    Http404,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from itertools import chain
from . import forms

from inventory.models import Item, Location
from login.models import User as myUser
from trace_item.models import ItemLog

from urllib.parse import quote


class IndexView(generic.View):
    def get(self, request):
        return render(request, 'inventory/index.html')


class ItemsView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return render(request, 'inventory/index.html')
        else:
            return super(ItemsView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        item_list = get_my_list(tmp_user, Item.objects.all())
        paginator = Paginator(item_list, 20)
        page = request.GET.get('page')
        try:
            item_list = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            item_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            item_list = paginator.page(paginator.num_pages)
        return render(request, 'inventory/items.html', locals())


class AddItemView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return render(request, 'inventory/index.html')
        else:
            return super(AddItemView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        add_form = forms.AddItemForm()
        return render(request, 'inventory/add.html', locals())

    def post(self, request):
        add_form = forms.AddItemForm(request.POST)
        message = "请检查填写的内容！"
        if add_form.is_valid():
            tmp_user = myUser.objects.get(id=request.session.get('user_id'))
            name = add_form.cleaned_data['name']
            quantity = add_form.cleaned_data['quantity']
            unit = add_form.cleaned_data['unit']
            new_item = Item.objects.create(
                name=name,
                quantity=quantity,
                unit=unit,
                owner=tmp_user,
            )
            new_item.allowed_users.add(tmp_user)
            new_item.save()
            message = "添加成功！"
            return render(request, 'inventory/add.html', locals())
        else:
            return self.get(request)


class ItemView(generic.View):
    item = None
    tmp_user = None

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return render(request, 'inventory/index.html')
        else:
            user_id = request.session.get('user_id')
            tmp_user = myUser.objects.get(id=user_id)
            self.item = get_my_item(tmp_user, kwargs.get('id'))
            return super(ItemView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        use_item_form = forms.UseItemForm()
        item = self.item
        return render(request, 'inventory/item.html', locals())

    def post(self, request, *args, **kwargs):
        use_item_form = forms.UseItemForm(request.POST)
        if use_item_form.is_valid():
            quantity = float(use_item_form.cleaned_data['quantity'])
            if quantity > 0 and quantity <= self.item.quantity:
                log = ItemLog.objects.create(
                    operator=self.tmp_user,
                    location_from=self.item.location,
                    location_to=self.item.location,
                    quantity_from=self.item.quantity,
                    quantity_to=float(self.item.quantity) - quantity,
                )
                log.save()
                self.item.quantity = log.quantity_to
                self.item.save()
                message = "使用成功！"
            else:
                message = "使用数量有误！"
            item = self.item
            return render(request, 'inventory/item.html', locals())
        else:
            return self.get(request)


class LocationView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return render(request, 'inventory/index.html')
        else:
            return super(LocationView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        tmp_user = myUser.objects.get(id=user_id)
        location_id = kwargs.get('id')
        QRCode = "http://qr.liantu.com/api.php?text={0}".format(
            quote(request.build_absolute_uri()))
        if 'pending' in request.GET.keys():
            pending = get_my_item(tmp_user, request.GET['pending'])
        else:
            pending = None
        # root directory
        if location_id == None:
            all_locs = Location.objects.filter(parent=None)
        # other directory
        else:
            loc_now = get_my_loc(tmp_user, location_id)
            all_items = Item.objects.filter(location=loc_now)
            item_list = get_my_list(tmp_user, all_items)
            all_locs = loc_now.parentPath.all()
        loc_list = get_my_list(tmp_user, all_locs)
        return render(request, 'inventory/location.html', locals())


def put_item_to_location(request, item_id, location_id):
    user_id = request.session.get('user_id')
    tmp_user = myUser.objects.get(id=user_id)
    item = get_my_item(tmp_user, item_id)
    if int(location_id) != 0:
        # put item in
        location = get_my_loc(tmp_user, location_id)
        log = ItemLog.objects.create(
            operator=tmp_user,
            location_from=item.location,
            location_to=location,
            quantity_from=item.quantity,
            quantity_to=item.quantity,
        )
        log.save()
        item.location = log.location_to
        item.save()
        return redirect('inventory:location', location_id)
    else:
        # take item out
        log = ItemLog.objects.create(
            operator=tmp_user,
            location_from=item.location,
            location_to=None,
            quantity_from=item.quantity,
            quantity_to=item.quantity,
        )
        log.save()
        item.location = log.location_to
        item.save()
        return redirect('inventory:item', item.id)


def del_item(request, item_id):
    user_id = request.session.get('user_id')
    tmp_user = myUser.objects.get(id=user_id)
    item = get_my_item(tmp_user, item_id)
    if item.location != None:
        messages.error(request, "请先取出该物品！")
        return render(request, 'inventory/info.html', locals())
    item.allowed_users.remove(tmp_user)
    item.save()
    return redirect('inventory:items')


class InfoView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return render(request, 'inventory/index.html')
        else:
            return super(InfoView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'inventory/info.html', locals())


class AddItem2LocView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return render(request, 'inventory/index.html')
        else:
            return super(AddItem2LocView, self).dispatch(
                request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        tmp_user = myUser.objects.get(id=user_id)
        item_list = get_my_list(tmp_user, Item.objects.filter(location=None))
        location = get_my_loc(tmp_user, kwargs.get('id'))
        return render(request, 'inventory/additem2loc.html', locals())


def get_my_item(user_now, item_id):
    item = get_object_or_404(Item, id=item_id)
    # two cases: (admin) and (not admin)
    if not ((user_now.staff.all() & item.allowed_users.all()) or
            (item.allowed_users.filter(id=user_now.id))):
        raise Http404()
    return item


def get_my_loc(user_now, loc_id):
    loc = get_object_or_404(Location, id=loc_id)
    # two cases: (admin) and (not admin)
    if not ((user_now.staff.all() & loc.allowed_users.all()) or
            (loc.allowed_users.filter(id=user_now.id))):
        raise Http404()
    return loc


def get_my_list(user_now, all_obj):
    obj_list = all_obj.filter(allowed_users=user_now)
    users = user_now.staff.all()
    for user in users:
        obj_list = obj_list | all_obj.filter(allowed_users=user)
    return obj_list.distinct()
