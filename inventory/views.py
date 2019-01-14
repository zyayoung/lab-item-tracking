from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
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
            return redirect("/")
        else:
            self.user_id = request.session.get('user_id', None)
            return super(ItemsView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Item.objects.filter(user=self.user_id).order_by('-name')


class AddView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect("/")
        else:
            return super(AddView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        add_form = forms.AddItemForm()
        return render(request, 'inventory/add.html', locals())

    # TODO:add items properly
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
            return redirect('/add/')
        else:
            return self.get(request)


class ItemView(generic.DetailView):
    model = Item
    template_name = 'inventory/item.html'
    user_id = 0

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect("/")
        else:
            self.user_id = request.session.get('user_id', None)
            return super(ItemView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ItemView, self).get_context_data(**kwargs)
        item = context['item']
        context['permission'] = self.user_id in [
            user.id for user in item.user.all()
        ]
        return context


class LocationView(generic.ListView):
    model = Location
    template_name = 'inventory/location.html'
    context_object_name = 'location_list'
    myPath = None

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect("/")
        else:
            self.myPathList = kwargs['path'].split("/")
            return super(LocationView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        re = None
        try:
            if len(self.myPathList) <= 1:
                re = Location.objects.filter(parent=None)
            else:
                myPath = self.myPathList[-1]
                re = Location.objects.filter(path=myPath)[0].parentPath.all()
                if len(re) == 0:
                    item_id = Location.objects.filter(path=myPath).values('item_id')[0]['item_id']
                    re = Item.objects.filter(id=1)
                    print(re)
        except:
            pass
        finally:
            return re