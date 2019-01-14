from django.conf.urls import url

from inventory import views

app_name = 'inventory'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^index/$', views.IndexView.as_view(), name='index'),
    url(r'^materials/$', views.MaterialsView.as_view(), name='materials'),
    url(r'^add/$', views.AddView.as_view(), name='add'),
]
