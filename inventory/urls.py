from django.conf.urls import url

from inventory import views

app_name = 'inventory'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^index/$', views.IndexView.as_view(), name='index'),
    url(r'^items/$', views.ItemsView.as_view(), name='items'),
    url(r'^item/(?P<pk>\d+)/$', views.ItemView.as_view(), name='item'),
    url(r'^add/$', views.AddView.as_view(), name='add'),
]
