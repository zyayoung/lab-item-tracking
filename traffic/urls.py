from django.conf.urls import url

from traffic import views

app_name = 'traffic'

urlpatterns = [
    # url(r'^$', views.index),
    # url(r'^index/', views.index),
    url(r'pages', views.Pages.as_view()),
    url(r'calender', views.Calender.as_view()),
    url(r'users', views.Users.as_view()),
]
