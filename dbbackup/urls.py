from django.conf.urls import url

from . import views

app_name = 'dbbackup'

urlpatterns = [
    url('users', views.users, name='usersbk'),
    url('inventory', views.inventory, name='inventorybk'),
    url('log', views.log, name='logbk'),
]
