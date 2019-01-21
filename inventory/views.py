from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from inventory.utils import *
from inventory import forms

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
                quantity=0,
                unit=unit,
                owner=tmp_user,
            )
            new_item.allowed_users.add(tmp_user)
            set_quantity(new_item, quantity, tmp_user)
            message = "添加成功！"
            return redirect('inventory:item', new_item.id)
        else:
            return render(request, 'inventory/add.html', locals())


class ItemView(generic.View):
    item = None
    tmp_user = None

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return render(request, 'inventory/index.html')
        else:
            user_id = request.session.get('user_id')
            self.tmp_user = myUser.objects.get(id=user_id)
            self.item = get_my_item(self.tmp_user, kwargs.get('id'))
            return super(ItemView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        use_item_form = forms.UseItemForm()
        item = self.item
        tmp_user = self.tmp_user
        del_permission = item.owner == tmp_user or tmp_user.staff.filter(id=item.owner.id).exists()
        unlink_permission = not del_permission and item.allowed_users.filter(id=tmp_user.id).exists()
        return render(request, 'inventory/item.html', locals())

    def post(self, request, *args, **kwargs):
        use_item_form = forms.UseItemForm(request.POST)
        if use_item_form.is_valid():
            quantity = float(use_item_form.cleaned_data['quantity'])
            if 0 < quantity <= self.item.quantity:
                set_quantity(self.item, float(self.item.quantity) - quantity, self.tmp_user)
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
        current_location = Location.objects.get(id=location_id) if location_id else None
        current_location_str = current_location.__str__() if location_id else "root"
        QRCode = "http://qr.liantu.com/api.php?text={0}".format(
            quote(request.build_absolute_uri()))
        if 'pending' in request.GET.keys():
            pending = get_my_item(tmp_user, request.GET['pending'])
        else:
            pending = None
        # root directory
        if location_id == None:
            all_locs = Location.objects.filter(parent=None)
            allow_locs = get_my_list(tmp_user,all_locs)
            unallow_locs = all_locs.difference(allow_locs)
        # other directory
        else:
            loc_now = get_my_loc(tmp_user, location_id)
            all_items = Item.objects.filter(location=loc_now)
            item_list = get_my_list(tmp_user, all_items)
            all_locs = loc_now.parentPath.all()
            allow_locs = get_my_list(tmp_user,all_locs)
            unallow_locs = all_locs.difference(allow_locs)
        # loc_list = all_locs
        return render(request, 'inventory/location.html', locals())


def put_item_to_location(request, item_id, location_id):
    user_id = request.session.get('user_id')
    tmp_user = myUser.objects.get(id=user_id)
    item = get_my_item(tmp_user, item_id)
    if int(location_id) != 0:
        # put item in
        location = get_my_loc(tmp_user, location_id)
        set_location(item, location, tmp_user)
        return redirect('inventory:location', location_id)
    else:
        # take item out
        set_location(item, None, tmp_user)
        return redirect('inventory:item', item.id)


def del_item(request, item_id):
    user_id = request.session.get('user_id')
    tmp_user = myUser.objects.get(id=user_id)
    item = get_my_item(tmp_user, item_id)
    if not (item.owner == tmp_user or tmp_user.staff.filter(id=item.owner.id).exists()):
        messages.error(request, "只有创建人（" + item.owner.name + "）及其管理员可以删除物品！")
        return render(request, 'inventory/info.html', locals())
    item.allowed_users.clear()
    set_location(item, None, tmp_user)
    set_quantity(item, 0, tmp_user)
    return redirect('inventory:items')


def unlink_item(request, item_id):
    user_id = request.session.get('user_id')
    tmp_user = myUser.objects.get(id=user_id)
    item = get_my_item(tmp_user, item_id)
    if not item.allowed_users.filter(id=tmp_user.id).exists():
        messages.error(request, "您没有关联该物品！")
        return render(request, 'inventory/info.html', locals())
    elif item.owner == tmp_user or tmp_user.staff.filter(id=item.owner.id).exists():
        messages.error(request, "您不能取消关联该物品！")
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
