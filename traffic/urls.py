from django.conf.urls import url

from traffic import views

app_name = 'traffic'

urlpatterns = [
    # url(r'^$', views.index),
    # url(r'^index/', views.index),
    url(r'^traffic/pages/$', views.page_view, name='performance'),
    url(r'^traffic/calender/$', views.calender_view, name='calender'),
    url(r'^traffic/users/$', views.users_view, name='userAnalyze'),
    url(r'^traffic/locations/$', views.locations_view, name='locationAnalyze'),
]
