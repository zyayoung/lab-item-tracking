from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from inventory.utils import *
from inventory import forms

from inventory.models import Item, Location, LocationPermissionApplication, ItemTemplate
from login.models import User as myUser
from personal.utils import get_others_request_list
from urllib.parse import quote
from traffic.utils import build_loc_tree

OBJ_PER_PAGE = 50


class IndexView(generic.View):
    def get(self, request):
        user_id = request.session.get('user_id')
        if user_id:
            tmp_user = myUser.objects.get(id=user_id)
            others_request_list_count = get_others_request_list(
                tmp_user).filter(
                    approved=False, rejected=False).count()
        return render(request, 'inventory/index.html', locals())


class ItemsView(generic.View):
    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        item_list = get_my_list(tmp_user, Item.objects.all())
        keyword = request.GET.get('q')
        if keyword:
            keyword_iri = quote(keyword)
            item_list = item_list.filter(name__contains=keyword)
        paginator = Paginator(item_list, OBJ_PER_PAGE)
        page = request.GET.get('page', 1)
        try:
            item_list = paginator.page(page)
        except EmptyPage:
            item_list = paginator.page(paginator.num_pages)
        return render(request, 'inventory/items.html', locals())


class AddItemView(generic.View):
    def get_form(self, *args, **kwargs):
        return forms.AddItemForm(*args)

    def get(self, request):
        add_form = self.get_form()
        return render(request, 'inventory/add.html', locals())

    def post(self, request):
        add_form = self.get_form(request.POST)
        message = "请检查填写的内容！"
        if add_form.is_valid():
            tmp_user = myUser.objects.get(id=request.session.get('user_id'))
            name = add_form.cleaned_data['name']
            quantity = add_form.cleaned_data['quantity']
            unit = add_form.cleaned_data['unit']
            public = add_form.cleaned_data['public']
            new_item = Item.objects.create(
                name=name,
                quantity=0,
                unit=unit,
                owner=tmp_user,
                is_public=public,
                template=None,
            )
            new_item.allowed_users.add(tmp_user)
            set_quantity(new_item, quantity, tmp_user)
            message = "添加成功！"
            return redirect('inventory:edit', new_item.id)
        else:
            return render(request, 'inventory/add.html', locals())


class ItemView(generic.View):
    item = None
    tmp_user = None
    all_users = None
    message = None

    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        self.tmp_user = myUser.objects.get(id=user_id)
        self.item = get_my_item(self.tmp_user, kwargs.get('id'))
        self.all_users = myUser.objects.all()
        return super(ItemView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        message = self.message
        use_item_form = forms.UseItemForm()
        item = self.item
        tmp_user = self.tmp_user
        all_users = self.all_users
        del_permission = item.del_permission(tmp_user)
        unlink_permission = item.unlink_permission(tmp_user)
        return render(request, 'inventory/item.html', locals())

    def post(self, request, *args, **kwargs):
        item = self.item
        action = request.GET['action']
        use_item_form = forms.UseItemForm(request.POST)
        if action == 'item' and use_item_form.is_valid():
            tmp_user = self.tmp_user
            quantity = float(use_item_form.cleaned_data['quantity'])
            if 0 < quantity < self.item.quantity:
                set_quantity(self.item,
                             float(self.item.quantity) - quantity,
                             self.tmp_user)
                self.message = "使用成功！"
            else:
                self.message = "使用数量有误！"
        elif action == 'user':
            item.allowed_users.clear()
            item.allowed_users.add(item.owner)
            for user_id in request.POST.getlist('share'):
                item.allowed_users.add(myUser.objects.get(id=user_id))
            item.save()
            self.message = "保存成功！"
        return self.get(request, *args, **kwargs)


def template_ajax(request, *args, **kwargs):
    template_id = int(request.POST.get('id', 0))
    if template_id != 0:
        template = ItemTemplate.objects.get(id=template_id)
        extra_data = template.extra_data
        data = extra_data.get('data', {})
        edit_form = forms.EditItemForm(*args, data=extra_data)
    return render(request, 'inventory/editajax.html', locals())


class EditItemView(generic.View):
    tmp_user = None
    item = None

    def get_form(self, *args, **kwargs):
        _templates = ItemTemplate.objects.all()
        choices = [(0, '--')]
        if _templates.exists():
            choices.extend([(t.id, t.name) for t in _templates.all()])
        return forms.ChooseTemplateForm(*args, choices=choices)

    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        tmp_user = myUser.objects.get(id=user_id)
        item = get_my_item(tmp_user, kwargs.get('item_id'))
        choose_form = self.get_form()
        add_form = forms.AddItemForm()
        return render(request, 'inventory/edit.html', locals())

    def post(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        item = get_my_item(tmp_user, kwargs.get('item_id'))
        message = "请检查填写的内容！"
        add_form = forms.AddItemForm(request.POST)
        if add_form.is_valid():
            item.name = add_form.cleaned_data['name']
            item.quantity = add_form.cleaned_data['quantity']
            item.unit = add_form.cleaned_data['unit']
        else:
            return render(request, 'inventory/edit.html', locals())
        choose_form = self.get_form(request.POST)
        if choose_form.is_valid():
            data = {}
            template_id = int(choose_form.cleaned_data['template'])
            if template_id != 0:
                template = ItemTemplate.objects.get(id=template_id)
                extra_data = template.extra_data
                edit_form = forms.EditItemForm(request.POST, data=extra_data)
                if edit_form.is_valid():
                    for idx, (key,
                              value) in enumerate(template.extra_data.items()):
                        data[key] = edit_form.cleaned_data[key.replace(
                            ' ', '_')]
            else:
                template = None
            item.extra_data = data
            item.template = template
        else:
            return render(request, 'inventory/edit.html', locals())
        item.save()
        message = "修改成功！"
        return redirect('inventory:item', item.id)


class LocationView(generic.View):
    tmp_user = None
    location_id = None
    message = None

    def dispatch(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        self.tmp_user = myUser.objects.get(id=user_id)
        self.location_id = kwargs.get('id')
        return super(LocationView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        message = self.message
        tmp_user = self.tmp_user
        location_id = self.location_id
        QRCode = "http://qr.liantu.com/api.php?text={0}".format(
            quote(request.build_absolute_uri()))
        if tmp_user.is_superadmin:
            add_loc_form = forms.AddLocationForm()
        if 'pending' in request.GET.keys():
            pending = get_my_item(tmp_user, request.GET['pending'])
        else:
            pending = None
        if location_id:
            try:
                loc_now = get_my_loc(tmp_user, location_id)
                loc_now_str = loc_now.__str__()
            except Http404:
                return redirect('inventory:applyloc', location_id)
            all_items = Item.objects.filter(location=loc_now)
            all_locs = loc_now.location_children.all()
            item_list = get_my_list(tmp_user, all_items)
            paginator = Paginator(item_list, OBJ_PER_PAGE)
            page = request.GET.get('page')
            try:
                item_list = paginator.page(page)
            except PageNotAnInteger:
                item_list = paginator.page(1)
            except EmptyPage:
                item_list = paginator.page(paginator.num_pages)
        # root directory
        else:
            loc_now = None
            loc_now_str = 'root'
            all_locs = Location.objects.filter(parent=None)
        allow_locs = get_my_list(tmp_user, all_locs)
        unallow_locs = all_locs.difference(allow_locs)

        # Fancy charts
        # loc_node, item_count = build_loc_tree(loc_now, count=False, user=tmp_user, depth=2, link=True)
        return render(request, 'inventory/location.html', locals())

    def post(self, request, *args, **kwargs):
        tmp_user = self.tmp_user
        location_id = self.location_id
        if not tmp_user.is_superadmin:
            raise Http404()
        add_loc_form = forms.AddLocationForm(request.POST)
        if add_loc_form.is_valid():
            loc_now = get_my_loc(tmp_user,
                                 location_id) if location_id else None
            path = add_loc_form.cleaned_data['name']
            new_location = Location.objects.create(
                path=path,
                parent=loc_now,
                is_public=True,
            )
            new_location.save()
            self.message = "新建成功！"
            return self.get(request, *args, **kwargs)


def put_item_to_location(request, item_id, location_id):
    user_id = request.session.get('user_id')
    tmp_user = myUser.objects.get(id=user_id)
    item = get_my_item(tmp_user, item_id)
    if int(location_id) != 0:
        # put item in
        location = get_my_loc(tmp_user, location_id)
        set_location(item, location, tmp_user)
        return redirect('inventory:location', location_id)
    else:
        # take item out
        set_location(item, None, tmp_user)
        return redirect('inventory:item', item.id)


def del_item(request, item_id):
    user_id = request.session.get('user_id')
    tmp_user = myUser.objects.get(id=user_id)
    item = get_my_item(tmp_user, item_id)
    if not item.del_permission(tmp_user):
        messages.error(request, "只有创建人（" + item.owner.name + "）及其管理员可以删除物品！")
        return render(request, 'inventory/info.html', locals())
    item.allowed_users.clear()
    item.is_public = False
    set_location(item, None, tmp_user)
    set_quantity(item, 0, tmp_user)
    return redirect('inventory:items')


def unlink_item(request, item_id):
    user_id = request.session.get('user_id')
    tmp_user = myUser.objects.get(id=user_id)
    item = get_my_item(tmp_user, item_id)
    if item.unlink_permission(tmp_user):
        messages.error(request, "您不能取消关联该物品！")
        return render(request, 'inventory/info.html', locals())
    item.allowed_users.remove(tmp_user)
    item.save()
    return redirect('inventory:items')


class InfoView(generic.View):
    def get(self, request):
        return render(request, 'inventory/info.html', locals())


class AddItem2LocView(generic.View):
    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        tmp_user = myUser.objects.get(id=user_id)
        location = get_my_loc(tmp_user, kwargs.get('id'))
        item_list = get_my_list(tmp_user, Item.objects.filter(location=None))
        paginator = Paginator(item_list, OBJ_PER_PAGE)
        page = request.GET.get('page')
        try:
            item_list = paginator.page(page)
        except PageNotAnInteger:
            item_list = paginator.page(1)
        except EmptyPage:
            item_list = paginator.page(paginator.num_pages)
        return render(request, 'inventory/additem2loc.html', locals())


class Apply4Loc(generic.View):
    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        tmp_user = myUser.objects.get(id=user_id)
        loc_id = kwargs.get('item_id')
        loc = get_object_or_404(Location, id=loc_id)
        try:
            get_my_loc(tmp_user, loc_id)
        except Http404:
            apply_form = forms.ApplyLocationForm()
            return render(request, 'inventory/location_apply.html', locals())
        return redirect('inventory:location', loc_id)

    def post(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        tmp_user = myUser.objects.get(id=user_id)
        loc_id = kwargs.get('item_id')
        loc = get_object_or_404(Location, id=loc_id)
        try:
            get_my_loc(tmp_user, loc_id)
        except Http404:
            apply_form = forms.ApplyLocationForm(request.POST)
            message = "请检查填写的内容！"
            if apply_form.is_valid():
                if LocationPermissionApplication.objects.filter(
                        applicant=tmp_user,
                        location=loc,
                        approved=False,
                        rejected=False,
                ).exists():
                    message = "请勿重复提交"
                else:
                    new_form = LocationPermissionApplication.objects.create(
                        applicant=tmp_user,
                        location=loc,
                        explanation=apply_form.cleaned_data['note'],
                    )
                    new_form.save()
                    message = "提交成功"
                return render(request, 'inventory/location_apply.html',
                              locals())
            else:
                return self.get(request)
        return redirect('inventory:location', loc_id)
