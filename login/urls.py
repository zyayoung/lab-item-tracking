from django.conf.urls import url

from login import views

app_name = 'login'

urlpatterns = [
    # url(r'^$', views.index),
    # url(r'^index/', views.index),
    url(r'^login/', views.login),
    url(r'^register/', views.register),
    url(r'^logout/', views.logout),
]
