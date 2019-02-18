from django.conf.urls import url

from personal import views

app_name = 'personal'

urlpatterns = [
    url(r'^personal/$', views.UserView.as_view(), name='index'),
    url(r'^personal/settings/$', views.SettingsView.as_view(), name='settings'),
    url(r'^personal/(?P<id>\d+)/$', views.UserView.as_view(), name='user'),
    url(r'^personal/locreq/$', views.LocReqView.as_view(), name='locreq'),
    url(r'^personal/mylocreq/$', views.MyLocReqView.as_view(), name='mylocreq'),
    url(r'^personal/locreq/ajax/$', views.ajax_submit),
]
