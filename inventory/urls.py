from django.conf.urls import url

from inventory import views

app_name = 'inventory'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^index/$', views.IndexView.as_view(), name='index'),
    url(r'^orders/$', views.OrdersView.as_view(), name='orders'),
    url(r'^orders/(?P<pk>\d+)/$', views.OrderView.as_view(), name='order'),
    url(r'^materials/$', views.MaterialsView.as_view(), name='materials'),
    url(r'^item/(?P<pk>\d+)/$', views.ItemView.as_view(), name='item'),
    url(r'^add/$', views.AddView.as_view(), name='add'),
]
