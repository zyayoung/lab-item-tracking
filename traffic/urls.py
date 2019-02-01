from django.conf.urls import url

from traffic import views

app_name = 'traffic'

urlpatterns = [
    # url(r'^$', views.index),
    # url(r'^index/', views.index),
    url(r'^traffic/pages/$', views.Pages.as_view(), name='performance'),
    url(r'^traffic/calender/$', views.Calender.as_view(), name='calender'),
    url(r'^traffic/users/$', views.Users.as_view(), name='userAnalyze'),
    url(r'^traffic/locations/$', views.Locations.as_view(), name='locationAnalyze'),
]
