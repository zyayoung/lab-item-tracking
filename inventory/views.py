from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from . import forms

from inventory.models import Item, Location
from login.models import User as myUser


class IndexView(generic.View):
    def get(self, request):
        return render(request, 'inventory/index.html')


class ItemsView(generic.ListView):
    template_name = 'inventory/items.html'
    context_object_name = 'item_list'
    user_id = 0

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect('inventory:index')
        else:
            self.user_id = request.session.get('user_id', None)
            return super(ItemsView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Item.objects.filter(user=self.user_id).order_by('-name')


class AddView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect('inventory:index')
        else:
            return super(AddView, self).dispatch(request, *args, **kwargs)

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
            return redirect('inventory:add')
        else:
            return self.get(request)


class ItemView(generic.DetailView):
    model = Item
    template_name = 'inventory/item.html'
    user_id = 0

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect('inventory:index')
        else:
            self.user_id = request.session.get('user_id', None)
            return super(ItemView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ItemView, self).get_context_data(**kwargs)
        item = context['item']
        context['permission'] = self.user_id in [
            user.id for user in item.user.all()
        ]
        if not context['permission']:
            return redirect('inventory:index')
        return context


class LocationView(generic.View):
    template_name = 'inventory/location.html'
    context_object_name = 'location_list'
    myPath = None
    user_id = 0

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect('inventory:index')
        else:
            # self.myPathList = kwargs['path'].split("/")
            self.user_id = request.session.get('user_id', None)
            return super(LocationView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        location_id = kwargs.get('id')
        location = None
        location_list = None
        item_list = None
        permission = False
        pending = get_object_or_404(
            Item, pk=request.
            GET['pending']) if 'pending' in request.GET.keys() else None
        try:
            if location_id == None:
                location_list = Location.objects.filter(parent=None)
            else:
                location = Location.objects.filter(id=location_id)[0]
                permission = request.session.get('user_id', None) in [
                    user.id for user in location.allowed_users.all()
                ]
                location_list = location.parentPath.all()
                # if len(location_list) == 0:
                item_list = Item.objects.filter(
                    location=location, user=self.user_id)
        except:
            messages.error(request, "访问位置出现错误！")
            return redirect('inventory:info')
        return render(request, 'inventory/location.html', locals())


def put_item_to_location(request, item_pk, location_id):
    user_id = request.session.get('user_id', None)
    item = get_object_or_404(Item, pk=item_pk)
    if not user_id in [user.id for user in item.user.all()]:
        messages.error(request, "您没有更改该物品的权限！")
        return redirect('inventory:info')
    if int(location_id) != 0:
        print(location_id)
        location = get_object_or_404(Location, pk=location_id)
        if not user_id in [user.id for user in location.allowed_users.all()]:
            messages.error(request, "您没有更改该位置的权限！")
            return redirect('inventory:info')
        item.location = location
        item.save()
        return redirect('inventory:location', location_id)
    else:
        item.location = None
        item.save()
        return redirect('inventory:item', item.id)


class InfoView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect('inventory:index')
        else:
            return super(InfoView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'inventory/info.html', locals())

class AddItem2LocView(generic.View):
    model = Item
    template_name = 'inventory/additem2loc.html'
    context_object_name = 'item_list'

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect('inventory:index')
        else:
            self.user_id = request.session.get('user_id', None)
            return super(AddItem2LocView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        item_list = Item.objects.filter(location=None, user=self.user_id)
        location_id = kwargs.get('id')
        location = get_object_or_404(Location, pk=location_id)
        return render(request, 'inventory/additem2loc.html', locals())