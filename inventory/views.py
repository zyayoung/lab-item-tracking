from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.contrib import messages
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
        item_list = Item.objects.filter(
            user=request.session.get('user_id', None))
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
                myUser.objects.get(id=request.session['user_id']))
            new_item.save()
            message = "添加成功！"
            return render(request, 'inventory/add.html', locals())
        else:
            return self.get(request)


class ItemView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return render(request, 'inventory/index.html')
        else:
            return super(ItemView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id', None)
        item = get_object_or_404(Item, pk=kwargs.get('pk'))
        if not item.user.filter(id=user_id):
            messages.error(request, "您没有访问该物品的权限！")
            return render(request, 'inventory/info.html', locals())
        use_item_form = forms.UseItemForm()
        return render(request, 'inventory/item.html', locals())

    def post(self, request, *args, **kwargs):
        user_id = request.session.get('user_id', None)
        item = get_object_or_404(Item, pk=kwargs.get('pk'))
        if not item.user.filter(id=user_id):
            messages.error(request, "您没有访问该物品的权限！")
            return render(request, 'inventory/info.html', locals())
        use_item_form = forms.UseItemForm(request.POST)
        if use_item_form.is_valid():
            quantity = float(use_item_form.cleaned_data['quantity'])
            if quantity > 0 and quantity <= item.quantity:
                item.quantity = float(item.quantity) - quantity
                item.save()
                message = "使用成功！"
            else:
                message = "使用数量有误！"
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
        user_id = request.session.get('user_id', None)
        location_id = kwargs.get('id')
        location_list = None
        item_list = None
        QRCode = "http://qr.liantu.com/api.php?text={0}".format(
            quote(request.build_absolute_uri()))
        if 'pending' in request.GET.keys():
            pending = get_object_or_404(
                Item, pk=request.GET['pending'], user=user_id)
        else:
            pending = None
        try:
            # root directory
            if location_id == None:
                location_list = Location.objects.filter(
                    parent=None, allowed_users=user_id)
            # other directory
            else:
                location = Location.objects.filter(id=location_id)[0]
                location_list = location.parentPath.filter(
                    allowed_users=user_id)
                if not location.allowed_users.filter(id=user_id):
                    raise
                item_list = Item.objects.filter(
                    location=location, user=user_id)
        except:
            messages.error(request, "访问位置出现错误！")
            return render(request, 'inventory/info.html', locals())
        return render(request, 'inventory/location.html', locals())


def put_item_to_location(request, item_pk, location_id):
    user_id = request.session.get('user_id', None)
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
    user_id = request.session.get('user_id', None)
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
        user_id = request.session.get('user_id', None)
        item_list = Item.objects.filter(location=None, user=user_id)
        location_id = kwargs.get('id')
        location = get_object_or_404(Location, pk=location_id)
        return render(request, 'inventory/additem2loc.html', locals())