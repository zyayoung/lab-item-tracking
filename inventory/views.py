from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from inventory.utils import *
from inventory import forms
import re

from inventory.models import Item, Location, LocationPermissionApplication, ItemTemplate
from login.models import User as myUser
from personal.utils import get_others_request_list
from urllib.parse import quote

OBJ_PER_PAGE = 50


class IndexView(generic.View):
    def get(self, request):
        user_id = request.session.get('user_id')
        if user_id:
            tmp_user = myUser.objects.get(id=user_id)
            others_request_list_count = get_others_request_list(
                tmp_user).filter(closed=False).count()
        return render(request, 'inventory/index.html', locals())


class ItemsView(generic.View):
    def get(self, request, *args, **kwargs):
        is_property = 'prop' in request.path
        name = "物品属性" if is_property else "物品"
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        item_list = get_my_list(
            tmp_user, Item.objects.filter(template__is_property=is_property))
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
    def get(self, request):
        action = "新建"
        if 'template' in request.GET.keys() and 'select_id' in request.GET.keys():
            template = get_object_or_404(ItemTemplate, name=request.GET.get('template', ''))
            select_id = request.GET.get('select_id', '')
            is_popup = True
            is_property = template.is_property
            template_id = template.id
        else:
            is_property = 'prop' in request.path
        name = "物品属性" if is_property else "物品"
        choose_form = forms.ChooseTemplateForm(is_property=is_property)
        add_form = forms.AddItemForm()
        return render(request, 'inventory/edit.html', locals())

    def post(self, request):
        action = "新建"
        is_property = 'prop' in request.path
        name = "物品属性" if is_property else "物品"
        message = "请检查填写的内容！"
        add_form = forms.AddItemForm(request.POST)
        if add_form.is_valid():
            tmp_user = myUser.objects.get(id=request.session.get('user_id'))
            name = add_form.cleaned_data['name']
            public = add_form.cleaned_data['public']
            item = Item.objects.create(
                name=name,
                owner=tmp_user,
                is_public=public,
                template=None,
            )
            item.allowed_users.add(tmp_user)
        else:
            return render(request, 'inventory/edit.html', locals())
        choose_form = forms.ChooseTemplateForm(request.POST)
        if choose_form.is_valid():
            data = {}
            template_id = int(choose_form.cleaned_data['template'])
            template = ItemTemplate.objects.get(id=template_id)
            extra_data = template.extra_data
            edit_form = forms.EditItemForm(
                request.POST, data=extra_data, user=tmp_user)
            if edit_form.is_valid():
                for dictionary in template.extra_data:
                    data[dictionary['name']] = edit_form.cleaned_data[
                        dictionary['name'].replace(' ', '_')]
            set_extradata(item, template, data, tmp_user)
        else:
            return render(request, 'inventory/edit.html', locals())
        item.save()
        message = "新建成功！"
        if request.POST.get('is_popup', False):
            select_id = request.POST.get('select_id', '')
            return render(request, 'inventory/fill_form_in_parent.html',
                          locals())
        return redirect('inventory:item', item.id)


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
        item = self.item
        tmp_user = self.tmp_user
        all_users = self.all_users
        extra_info = []
        item_keys = list(item.extra_data.keys())
        if item.template:
            for data in item.template.extra_data:
                filled = False
                if data['name'] in item_keys:
                    data_name = data['name']
                    item_keys.remove(data_name)
                    if item.extra_data[data['name']]:
                        if data['type'] not in [
                                'bool', 'int', 'float', 'text'
                        ]:
                            try:
                                if int(item.extra_data[data_name]) != 0:
                                    extra_info.append(
                                        (data_name, {
                                            'data':
                                            get_my_item(
                                                tmp_user,
                                                item.extra_data[data_name]),
                                            'type':
                                            'link',
                                        }))
                                else:
                                    extra_info.append((data['name'], {
                                        'data': '--',
                                        'type': 'plain'
                                    }))
                            except Http404:
                                extra_info.append((data_name, {
                                    'data': '您没有访问此物品的权限',
                                    'type': 'warning',
                                }))
                        else:
                            extra_info.append((data_name, {
                                'data':
                                item.extra_data[data_name],
                                'type':
                                'plain',
                            }))
                        filled = True
                if not filled:
                    if data['required']:
                        extra_info.append((data['name'], {
                            'data': '缺失必填属性',
                            'type': 'warning',
                        }))
                    else:
                        extra_info.append((data['name'], {
                            'data': '--',
                            'type': 'plain'
                        }))

        for key in item_keys:
            if item.extra_data[key]:
                extra_info.append((key, {
                    'data': item.extra_data[key],
                    'type': 'extra'
                }))
        relation_info = {}
        for key, values in item.related_items.items():
            _items = []
            for value in values:
                try:
                    item = get_my_item(tmp_user, value)
                    _items.append(item)
                except Http404():
                    pass
            relation_info[key.replace('__', '->')] = _items
        del_permission = item.del_permission(tmp_user)
        unlink_permission = item.unlink_permission(tmp_user)
        return render(request, 'inventory/item.html', locals())

    def post(self, request, *args, **kwargs):
        item = self.item
        action = request.GET['action']
        if action == 'user':
            item.allowed_users.clear()
            item.allowed_users.add(item.owner)
            for user_id in request.POST.getlist('share'):
                item.allowed_users.add(myUser.objects.get(id=user_id))
            item.save()
            self.message = "保存成功！"
        return self.get(request, *args, **kwargs)


def template_ajax(request, *args, **kwargs):
    user_id = request.session.get('user_id')
    tmp_user = myUser.objects.get(id=user_id)
    template_id = int(request.POST.get('id', 0))
    if template_id != 0:
        template = ItemTemplate.objects.get(id=template_id)
        extra_data = template.extra_data
        edit_form = forms.EditItemForm(*args, data=extra_data, user=tmp_user)
    return render(request, 'inventory/editajax.html', locals())


class EditItemView(generic.View):
    tmp_user = None
    item = None

    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        tmp_user = myUser.objects.get(id=user_id)
        item = get_my_item(tmp_user, kwargs.get('item_id'))
        template_id = item.template.id
        is_property = item.template.is_property
        is_edit = True
        name = "属性" if is_property else "物品"
        action = "编辑"
        if not item.del_permission(tmp_user):
            messages.error(request,
                           "只有创建人（{}）及其管理员可以编辑物品！".format(item.owner.name))
            return render(request, 'inventory/info.html', locals())
        choose_form = forms.ChooseTemplateForm(is_property=is_property)
        add_form = forms.AddItemForm()
        return render(request, 'inventory/edit.html', locals())

    def post(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        item = get_my_item(tmp_user, kwargs.get('item_id'))
        is_property = item.template.is_property
        name = "属性" if is_property else "物品"
        action = "编辑"
        if not item.del_permission(tmp_user):
            messages.error(request,
                           "只有创建人（{}）及其管理员可以编辑物品！".format(item.owner.name))
            return render(request, 'inventory/info.html', locals())
        message = "请检查填写的内容！"
        add_form = forms.AddItemForm(request.POST)
        if add_form.is_valid():
            item.name = add_form.cleaned_data['name']
            item.is_public = add_form.cleaned_data['public']
        else:
            return render(request, 'inventory/edit.html', locals())
        choose_form = forms.ChooseTemplateForm(request.POST)
        if choose_form.is_valid():
            data = {}
            template_id = int(choose_form.cleaned_data['template'])
            template = ItemTemplate.objects.get(id=template_id)
            extra_data = template.extra_data
            edit_form = forms.EditItemForm(
                request.POST, data=extra_data, user=tmp_user)
            if edit_form.is_valid():
                for dictionary in template.extra_data:
                    data[dictionary['name']] = edit_form.cleaned_data[
                        dictionary['name'].replace(' ', '_')]
            set_extradata(item, template, data, tmp_user)
        else:
            return render(request, 'inventory/edit.html', locals())
        if 'save_as_new' in request.POST:
            new_item = Item.objects.create(
                name=item.name,
                attribute=item.attribute,
                related_items=item.related_items,
                location=None,
                owner=tmp_user,
                is_public=item.is_public,
            )
            set_extradata(new_item, template, item.extra_data, tmp_user)
            for user in item.allowed_users.all():
                new_item.allowed_users.add(user)
            new_item.save()
        else:
            item.save()
        message = "修改成功！"
        return redirect('inventory:item', item.id)


class TemplatesView(generic.View):
    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        if not tmp_user.is_superadmin:
            raise Http404()
        template_list = ItemTemplate.objects.all()
        keyword = request.GET.get('q')
        if keyword:
            keyword_iri = quote(keyword)
            template_list = template_list.filter(name__contains=keyword)
        paginator = Paginator(template_list, OBJ_PER_PAGE)
        page = request.GET.get('page', 1)
        try:
            template_list = paginator.page(page)
        except EmptyPage:
            template_list = paginator.page(paginator.num_pages)
        return render(request, 'inventory/templates.html', locals())


class TemplateView(generic.View):
    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        template = get_object_or_404(ItemTemplate, id=kwargs.get('id'))
        export_keys = get_export_keys(template)
        all_objs = get_my_list(tmp_user, Item.objects.filter(template=template))
        full_info = [get_export_values(template, obj) for obj in all_objs]
        return render(request, 'inventory/template.html', locals())


class AddTemplateView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        if not tmp_user.is_superadmin:
            raise Http404()
        return super(AddTemplateView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        add_form = forms.AddTemplateForm()
        is_property = request.GET.get('property') is not None
        return render(request, 'inventory/template_add.html', locals())

    def post(self, request):
        add_form = forms.AddTemplateForm(request.POST)
        message = "请检查填写的内容！"
        if add_form.is_valid():
            name = add_form.cleaned_data['name']
            new_template = ItemTemplate.objects.create(
                name=name,
                is_property=request.GET.get('property') is not None,
            )
            new_template.save()
            message = "新建成功！"
            return redirect('inventory:template_edit', new_template.id)
        else:
            return render(request, 'inventory/template_add.html', locals())


class EditTemplateView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        if not tmp_user.is_superadmin:
            raise Http404()
        return super(EditTemplateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        template = get_object_or_404(ItemTemplate, id=kwargs.get('id'))
        edit_form = forms.EditTemplateForm()
        choices = ["text", "float", "int", "bool"]
        choices.extend([
            name[0] for name in ItemTemplate.objects.all().values_list('name')
        ])
        return render(request, 'inventory/template_edit.html', locals())

    def post(self, request, *args, **kwargs):
        choices = ["text", "float", "int", "bool"]
        choices.extend([
            name[0] for name in ItemTemplate.objects.all().values_list('name')
        ])
        message = "请检查填写的内容！"
        template = get_object_or_404(ItemTemplate, id=kwargs.get('id'))
        my_list = []
        idx_list = []
        template.key_name = request.POST.get('key_name', '名称')
        for key in request.POST.keys():
            index = re.findall(r"^name_(\d+)$", key)
            if index:
                idx_list.append(int(index[0]))
        for index in sorted(idx_list):
            if not request.POST.get('name_{}'.format(index)):
                continue
            if not request.POST.get('type_{}'.format(index), '') in choices:
                messages = "无此类型：" + request.POST.get('type_{}'.format(index),
                                                      '')
                return render(request, 'inventory/template_edit.html',
                              locals())
            my_list.append({
                'name':
                request.POST.get('name_{}'.format(index)),
                'type':
                request.POST.get('type_{}'.format(index), ''),
                'required':
                bool(int(request.POST.get('required_{}'.format(index), 0))),
                'placeholder':
                request.POST.get('placeholder_{}'.format(index), '')
            })
        template.extra_data = my_list
        template.save()
        message = "保存成功"
        return redirect('inventory:templates')


def del_template(request, template_id):
    tmp_user = myUser.objects.get(id=request.session.get('user_id'))
    if not tmp_user.is_superadmin:
        raise Http404()
    template = get_object_or_404(ItemTemplate, id=template_id)
    template.delete()
    return redirect('inventory:templates')


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
            all_items = Item.objects.filter(
                location=loc_now, template__is_property=False)
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
            public = add_loc_form.cleaned_data['public']
            if Location.objects.filter(
                    path=path,
                    parent=loc_now,
            ).exists():
                self.message = "路径名称重复！"
                return self.get(request, *args, **kwargs)
            new_location = Location.objects.create(
                path=path,
                parent=loc_now,
                is_public=public,
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
    is_property = item.template.is_property
    set_location(item, None, tmp_user)
    set_extradata(item, None, {}, tmp_user)
    item.delete()
    return redirect(
        'inventory:properties') if is_property else redirect(
            'inventory:items')


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
        item_list = get_my_list(
            tmp_user,
            Item.objects.filter(location=None, template__is_property=False))
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
                        closed=False,
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


def rebuild(request):
    rebuild_related()
    return redirect('inventory:index')