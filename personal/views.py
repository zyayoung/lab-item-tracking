from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from personal.utils import *

from login.models import User as myUser
from inventory.models import LocationPermissionApplication as LocPmsnApp


class IndexView(generic.View):
    def get(self, request, *args, **kwargs):
        user = myUser.objects.get(id=request.session.get('user_id'))
        staff_list = user.staff.all() if user.staff.exists() else None
        manager_list = user.staffUser.all() if user.staffUser.exists() else None
        if user.is_superadmin:
            permission = "超级管理员"
            request_list = get_request_list(user)
        elif staff_list:
            permission = "主管"
            request_list = get_request_list(user)
        else:
            permission = "员工"
        return render(request, 'personal/index.html', locals())

class UserView(generic.View):
    def get(self, request, *args, **kwargs):
        user = myUser.objects.get(id=kwargs.get('id'))
        staff_list = user.staff.all() if user.staff.exists() else None
        manager_list = user.staffUser.all() if user.staffUser.exists() else None
        if user.is_superadmin:
            permission = "超级管理员"
        elif staff_list:
            permission = "主管"
        else:
            permission = "员工"
        return render(request, 'personal/user.html', locals())
