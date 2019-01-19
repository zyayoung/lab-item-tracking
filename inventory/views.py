from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from itertools import chain
from . import forms

from inventory.models import Item, Location
from login.models import User as myUser

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
        all_item = Item.objects.all()
        item_list = all_item.filter(user=tmp_user)
        ids = tmp_user.staff.all()
        for _id in ids:
            item_list = item_list | all_item.filter(user=_id)
        item_list = item_list.distinct()
        item_list = item_list.distinct()
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
        if add_form.is_valid():  # 获取数据
            name = add_form.cleaned_data['name']
            quantity = add_form.cleaned_data['quantity']
            unit = add_form.cleaned_data['unit']
            new_item = Item.objects.create(
                name=name,
                quantity=quantity,
                unit=unit,
            )
            new_item.user.add(
                myUser.objects.get(id=request.session.get('user_id')))
            new_item.save()
            message = "添加成功！"
            return render(request, 'inventory/add.html', locals())
        else:
            return self.get(request)


class ItemView(generic.View):
    item = None

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return render(request, 'inventory/index.html')
        else:
            self.item = get_object_or_404(Item, pk=kwargs.get('pk'))
            tmp_user = myUser.objects.get(id=request.session.get('user_id'))
            # two cases: (admin) and (not admin)
            if not ((tmp_user.staff.all() & self.item.user.all()) or
                    (self.item.user.filter(id=tmp_user.id))):
                messages.error(request, "您没有访问该物品的权限！")
                return render(request, 'inventory/info.html', locals())
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
                self.item.quantity = float(self.item.quantity) - quantity
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
        loc_list = None
        item_list = None
        QRCode = "http://qr.liantu.com/api.php?text={0}".format(
            quote(request.build_absolute_uri()))
        if 'pending' in request.GET.keys():
            pending = get_object_or_404(
                Item, pk=request.GET['pending'], user=user_id)
        else:
            pending = None
        # root directory
        if location_id == None:
            all_location = Location.objects.filter(parent=None)
        # other directory
        else:
            loc_now = Location.objects.get(id=location_id)
            # two cases: (admin) and (not admin)
            if not ((tmp_user.staff.all() & loc_now.allowed_users.all()) or
                    (loc_now.allowed_users.filter(id=tmp_user.id))):
                messages.error(request, "访问位置出现错误！")
                return render(request, 'inventory/info.html', locals())
            all_location = loc_now.parentPath.all()
            item_list = Item.objects.filter(location=loc_now, user=user_id)
        loc_list = all_location.filter(allowed_users=user_id)
        ids = tmp_user.staff.all()
        for _id in ids:
            loc_list = loc_list | all_location.filter(allowed_users=_id)
            print(all_location.filter(allowed_users=_id))
        loc_list = loc_list.distinct()
        return render(request, 'inventory/location.html', locals())


def put_item_to_location(request, item_pk, location_id):
    user_id = request.session.get('user_id')
    item = get_object_or_404(Item, pk=item_pk)
    if not item.user.filter(id=user_id):
        messages.error(request, "您没有访问该物品的权限！")
        return render(request, 'inventory/info.html', locals())
    # put item in
    if int(location_id) != 0:
        # print(location_id)
        location = get_object_or_404(Location, pk=location_id)
        if not location.allowed_users.filter(id=user_id):
            messages.error(request, "您没有更改该位置的权限！")
            return render(request, 'inventory/info.html', locals())
        item.location = location
        item.save()
        return redirect('inventory:location', location_id)
    # take item out
    else:
        item.location = None
        item.save()
        return redirect('inventory:item', item.id)


def del_item(request, item_pk):
    user_id = request.session.get('user_id')
    item = get_object_or_404(Item, pk=item_pk)
    if not user_id in [user.id for user in item.user.all()]:
        messages.error(request, "您没有更改该物品的权限！")
        return render(request, 'inventory/info.html', locals())
    if item.location != None:
        messages.error(request, "请先取出该物品！")
        return render(request, 'inventory/info.html', locals())
    item.user.remove(user_id)
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
        item_list = Item.objects.filter(location=None, user=user_id)
        location_id = kwargs.get('id')
        location = get_object_or_404(Location, pk=location_id)
        return render(request, 'inventory/additem2loc.html', locals())