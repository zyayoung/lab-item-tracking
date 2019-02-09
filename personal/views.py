from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from personal.utils import *
from inventory.utils import get_my_loc

from login.models import User as myUser
from inventory.models import LocationPermissionApplication as LocPmsnApp

OBJ_PER_PAGE = 50


class UserView(generic.View):
    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        user_id = kwargs.get('id')
        if user_id:
            user = get_object_or_404(myUser, id=user_id)
        else:
            user = tmp_user
        staff_list = user.staff.all()
        manager_list = user.user_manager.all()
        permission = user.permission_str()
        return render(request, 'personal/user.html', locals())


class LocReqView(generic.View):
    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        if not tmp_user.is_superadmin and not tmp_user.staff.exists():
            return redirect('personal:mylocreq')
        others_request_list = get_others_request_list(tmp_user)
        others_request_list_count = others_request_list.filter(
            closed=False).count()
        paginator = Paginator(others_request_list, OBJ_PER_PAGE)
        page = request.GET.get('page')
        try:
            others_request_list = paginator.page(page)
        except PageNotAnInteger:
            others_request_list = paginator.page(1)
        except EmptyPage:
            others_request_list = paginator.page(paginator.num_pages)
        return render(request, 'personal/locreq.html', locals())


class MyLocReqView(generic.View):
    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        others_request_list_count = get_others_request_list(tmp_user).filter(
            closed=False).count()
        my_request_list = get_my_request_list(tmp_user)
        paginator = Paginator(my_request_list, OBJ_PER_PAGE)
        page = request.GET.get('page')
        try:
            my_request_list = paginator.page(page)
        except PageNotAnInteger:
            my_request_list = paginator.page(1)
        except EmptyPage:
            my_request_list = paginator.page(paginator.num_pages)
        return render(request, 'personal/mylocreq.html', locals())


def ajax_submit(request):
    re_dict = {'status': 1}
    tmp_user = myUser.objects.get(id=request.session.get('user_id'))
    req_id = int(request.POST.get('id'))
    result = int(request.POST.get('result'))
    req = get_object_or_404(LocPmsnApp, id=req_id)
    if req not in get_others_request_list(tmp_user):
        return JsonResponse(re_dict)
    try:
        get_my_loc(tmp_user, req.location.id)
    except Http404:
        return JsonResponse(re_dict)
    if result == 1:
        req.approve()
    elif result == 0:
        req.reject()
    req.auditor = tmp_user
    re_dict = {'status': 0}
    return JsonResponse(re_dict)
