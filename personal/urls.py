from django.conf.urls import url

from personal import views

app_name = 'personal'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<id>\d+)/$', views.UserView.as_view(), name='user'),
    url(r'^locreq/$', views.LocReqView.as_view(), name='locreq'),
    url(r'^mylocreq/$', views.MyLocReqView.as_view(), name='mylocreq'),
    url(r'^locreq/ajax/$', views.ajax_submit),
]
