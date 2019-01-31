"""lab_item_tracking URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.views.static import serve
from django.http import HttpResponse


SSL_CERTIFICATION_URL = r'^\.well-known/pki-validation/fileauth.txt$'


def ssl_certification(request):
    return HttpResponse('2019013000530848et5a8jwh9esmj3s5b1ez3dr94x1pj3n9l5jzmczx61yklhr9')


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^static/(?P<path>.*)$', serve,
        {'document_root': settings.STATIC_ROOT}, name='static'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^', include('inventory.urls')),
    url(r'^', include('login.urls')),
    url(r'^', include('trace_item.urls')),
    url(r'^', include('personal.urls')),
    url(r'^', include('traffic.urls')),
    url(r'^silk/', include('silk.urls', namespace='silk')),
    url(SSL_CERTIFICATION_URL, ssl_certification)
]
