from django.conf.urls import url

from trace_item import views

app_name = 'trace_item'

urlpatterns = [
    url(r'^item/(?P<id>\d+)/trace/$', views.TraceItemView.as_view(), name='trace'),
]
