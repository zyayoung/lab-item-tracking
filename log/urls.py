from django.conf.urls import url

from log import views

app_name = 'log'

urlpatterns = [
    url(r'^personal/(?P<id>\d+)/log/$', views.UserLogView.as_view(), name='user_log'),
    url(r'^item/(?P<id>\d+)/log/$', views.ItemLogView.as_view(), name='item_log'),
    url(r'^logs/$', views.LogsView.as_view(), name='logs'),
]
