from django.conf.urls import url

from trace_item import views

app_name = 'trace_item'

urlpatterns = [
    url(r'^item/(?P<id>\d+)/trace/$', views.TraceItemView.as_view(), name='traceItem'),
    url(r'^location/(?P<id>\d+)/trace/$', views.TraceLocationView.as_view(), name='traceLoc'),
    url(r'^personal/(?P<id>\d+)/trace/$', views.TraceUserView.as_view(), name='traceUser'),
]
