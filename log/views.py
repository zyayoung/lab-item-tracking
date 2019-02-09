from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from log.models import Log
from login.models import User as myUser
from django.views import generic
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from inventory.utils import get_my_item, get_my_loc, get_my_list, get_my_user

OBJ_PER_PAGE = 50


class UserLogView(generic.View):
    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        user = get_my_user(tmp_user, kwargs.get('id'))
        logs = Log.objects.filter(operator=user)
        if not 'all' in request.GET.keys():
            paginator = Paginator(logs, OBJ_PER_PAGE)
            page = request.GET.get('page')
            try:
                logs = paginator.page(page)
            except PageNotAnInteger:
                logs = paginator.page(1)
            except EmptyPage:
                logs = paginator.page(paginator.num_pages)
        return render(request, 'log/user_log.html', locals())


class ItemLogView(generic.View):
    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        item = get_my_item(tmp_user, kwargs.get('id'))
        logs = Log.objects.filter(category__contains='物品', obj_id=item.id)
        if not 'all' in request.GET.keys():
            paginator = Paginator(logs, OBJ_PER_PAGE)
            page = request.GET.get('page')
            try:
                logs = paginator.page(page)
            except PageNotAnInteger:
                logs = paginator.page(1)
            except EmptyPage:
                logs = paginator.page(paginator.num_pages)
        return render(request, 'log/item_log.html', locals())


class LogsView(generic.View):
    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        if not tmp_user.is_superadmin:
            raise Http404()
        logs = Log.objects.all()
        if not 'all' in request.GET.keys():
            paginator = Paginator(logs, OBJ_PER_PAGE)
            page = request.GET.get('page')
            try:
                logs = paginator.page(page)
            except PageNotAnInteger:
                logs = paginator.page(1)
            except EmptyPage:
                logs = paginator.page(paginator.num_pages)
        return render(request, 'log/logs.html', locals())