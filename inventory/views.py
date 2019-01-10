from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic

from inventory.models import Order, Item, Material

def index(request):
    return render(request, 'inventory/index.html')

class MaterialsView(generic.ListView):
    template_name = 'inventory/materials.html'
    context_object_name = 'material_list'
    def get_queryset(self):
        return Material.objects.order_by('-name')

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
        context['lineitems'] = context['order'].orderitem_set.order_by("item__vendor")
        return context


class ItemView(generic.DetailView):
    model = Item
    template_name = 'inventory/item.html'

    def get_context_data(self, **kwargs):
        context = super(ItemView, self).get_context_data(**kwargs)
        context['lineitems'] = context['item'].orderitem_set.order_by("order__order_date")
        return context
