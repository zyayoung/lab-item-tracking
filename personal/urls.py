from django.conf.urls import url

from personal import views

app_name = 'personal'

urlpatterns = [
    url(r'^personal/$', views.IndexView.as_view(), name='index'),
    url(r'^personal/(?P<id>\d+)/$', views.UserView.as_view(), name='user'),
    url(r'^personal/locreq/$', views.LocReqView.as_view(), name='locreq'),
]
