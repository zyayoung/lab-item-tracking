from django.conf.urls import url

from inventory import views

app_name = 'inventory'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^index/$', views.IndexView.as_view(), name='index'),
    url(r'^items/$', views.ItemsView.as_view(), name='items'),
    url(r'^item/(?P<pk>\d+)/$', views.ItemView.as_view(), name='item'),
    url(r'^item/(?P<item_pk>\d+)/del/$',
        views.del_item,
        name='delete'),
    url(r'^item/add/$', views.AddItemView.as_view(), name='add'),
    url(r'^location/(?P<id>\d+)/$',
        views.LocationView.as_view(),
        name='location'),
    url(r'^location/$', views.LocationView.as_view(), name='location_root'),
    url(r'^location/(?P<id>\d+)/add/$',
        views.AddItem2LocView.as_view(),
        name='additem2loc'),
    url(r'^put/(?P<item_pk>\d+)/(?P<location_id>\d+)/$',
        views.put_item_to_location,
        name='put'),
    url(r'^info/$', views.InfoView.as_view(), name='info'),
]
