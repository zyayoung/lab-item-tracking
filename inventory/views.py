from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from . import forms

from inventory.models import Order, Item, Material, Location, Unit
from login.models import User as myUser


class IndexView(generic.View):
    def get(self, request):
        return render(request, 'inventory/index.html')


class MaterialsView(generic.ListView):
    template_name = 'inventory/materials.html'
    context_object_name = 'material_list'
    user_id = 0

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect("/")
        else:
            self.user_id = request.session.get('user_id', None)
            return super(MaterialsView, self).dispatch(request, *args,
                                                       **kwargs)

    def get_queryset(self):
        return Material.objects.filter(user=self.user_id).order_by('-name')


class AddView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect("/")
        else:
            return super(AddView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        add_form = forms.AddForm()
        return render(request, 'inventory/add.html', locals())

    # TODO:add materials properly
    def post(self, request):
        add_form = forms.AddForm(request.POST)
        message = "请检查填写的内容！"
        if add_form.is_valid():  # 获取数据
            name = add_form.cleaned_data['name']
            location = add_form.cleaned_data['location']
            quantity = add_form.cleaned_data['quantity']
            new_material = Material.objects.create(
                name=name,
                location=Location.objects.create(),
                quantity=quantity,
                unit=Unit.objects.get(id=1),
                # user=myUser.objects.get(id=request.session['user_id']),
            )
            new_material.save()
            message = "添加成功！"
            return redirect('/add/')
        else:
            return self.get(request)


class OrdersView(generic.ListView):
    template_name = 'inventory/orders.html'
    context_object_name = 'order_list'

    def get_queryset(self):
        return Order.objects.order_by('-created')


class OrderView(generic.DetailView):
    model = Order
    template_name = 'inventory/order.html'

    def get_context_data(self, **kwargs):
        context = super(OrderView, self).get_context_data(**kwargs)
        context['lineitems'] = context['order'].orderitem_set.order_by(
            "item__vendor")
        return context


class ItemView(generic.DetailView):
    model = Item
    template_name = 'inventory/item.html'

    def get_context_data(self, **kwargs):
        context = super(ItemView, self).get_context_data(**kwargs)
        context['lineitems'] = context['item'].orderitem_set.order_by(
            "order__order_date")
        return context
