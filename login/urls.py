from django.conf.urls import url

from login import views

app_name = 'login'

urlpatterns = [
    # url(r'^$', views.index),
    # url(r'^index/', views.index),
    url(r'^login/', views.login, name='login'),
    url(r'^register/', views.register, name='register'),
    url(r'^logout/', views.logout, name='logout'),
]
