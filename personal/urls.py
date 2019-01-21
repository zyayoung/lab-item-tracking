from django.conf.urls import url

from personal import views

app_name = 'personal'

urlpatterns = [
    url(r'^personal/$', views.IndexView.as_view(), name='index'),
]
