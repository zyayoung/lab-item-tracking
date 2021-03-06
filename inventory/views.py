from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from inventory.utils import *
from inventory import forms
from log.utils import *
import re
import time
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
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
    message = None

    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        is_property = 'prop' in request.path
        template_queryset = ItemTemplate.objects.all()
        choose_form = forms.ChooseTemplateForm(
            is_property=is_property, template_queryset=template_queryset)
        name = _("物品属性") if is_property else _("物品")
        choices = choose_form.fields["template"].choices
        if 'filter' not in tmp_user.settings.keys():
            tmp_user.settings['filter'] = []
            tmp_user.save()
        user_filter = tmp_user.settings['filter']
        item_list = get_my_list(
            tmp_user,
            Item.objects.filter(template__is_property=is_property).exclude(
                template__id__in=user_filter))
        keyword = request.GET.get('q')
        if keyword:
            keyword_iri = quote(keyword)
            item_list = item_list.filter(name__contains=keyword)
        else:
            keyword = ''
        paginator = Paginator(item_list, OBJ_PER_PAGE)
        page = request.GET.get('page', 1)
        try:
            item_list = paginator.page(page)
        except EmptyPage:
            item_list = paginator.page(paginator.num_pages)
        return render(request, 'inventory/items.html', locals())

    def post(self, request, *args, **kwargs):
        action = request.GET['action']
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        if action == 'user':
            is_property = 'prop' in request.path
            template_queryset = ItemTemplate.objects.all()
            choose_form = forms.ChooseTemplateForm(
                is_property=is_property, template_queryset=template_queryset)
            choices = choose_form.fields["template"].choices
            settings = tmp_user.settings
            new_filter = [int(id) for id in request.POST.getlist('filter')]
            for key, value in choices:
                if key in settings['filter'] and key in new_filter:
                    settings['filter'].remove(key)
                elif key not in settings['filter'] and key not in new_filter:
                    settings['filter'].append(key)
            tmp_user.settings = settings
            tmp_user.save()
        return HttpResponseRedirect(request.path)


class AddItemView(generic.View):
    def get(self, request):
        action = "新建"
        action_translated = _(action) + ' '
        if 'template' in request.GET.keys(
        ) and 'select_id' in request.GET.keys():
            template = get_object_or_404(
                ItemTemplate, name=request.GET.get('template', ''))
            select_id = request.GET.get('select_id', '')
            is_popup = True
            is_property = template.is_property
            template_id = template.id
        else:
            is_property = 'prop' in request.path
        name = _("物品属性") if is_property else _("物品")
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        template_queryset = get_my_template_queryset(
            tmp_user, ItemTemplate.objects.all())
        choose_form = forms.ChooseTemplateForm(
            is_property=is_property, template_queryset=template_queryset)
        add_form = forms.AddItemForm()
        return render(request, 'inventory/edit.html', locals())

    def post(self, request):
        action = "新建"
        action_translated = _(action) + ' '
        is_property = 'prop' in request.path
        message = _("请检查填写的内容！")
        add_form = forms.AddItemForm(request.POST)
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        if add_form.is_valid():
            name = add_form.cleaned_data['name']
            custom_id = add_form.cleaned_data['custom_id']
            public = add_form.cleaned_data['public']
            item = Item.objects.create(
                name=name,
                custom_id=custom_id,
                owner=tmp_user,
                is_public=public,
                template=None,
            )
            add_log(tmp_user, item.id, '物品', '公开', 'False',
                    'True' if public else 'False')
            item.allowed_users.add(tmp_user)
            add_log(tmp_user, item.id, '物品', '白名单', '', tmp_user.name)
        else:
            return self.get(request)
        template_queryset = get_my_template_queryset(
            tmp_user, ItemTemplate.objects.all())
        choose_form = forms.ChooseTemplateForm(
            request.POST, template_queryset=template_queryset)
        if choose_form.is_valid():
            data = {}
            template_id = int(choose_form.cleaned_data['template'])
            template = ItemTemplate.objects.get(id=template_id)
            edit_form = forms.EditItemForm(
                request.POST, template=template, user=tmp_user)
            if edit_form.is_valid():
                for dictionary in template.extra_data:
                    data[dictionary['name']] = edit_form.cleaned_data[
                        dictionary['name'].replace(' ', '_')]
                    if data[dictionary['name']]:
                        if dictionary['type'] == 'link':
                            data[dictionary['name']] = int(
                                data[dictionary['name']])
                        elif dictionary['type'] == 'date':
                            data[dictionary['name']] = data[
                                dictionary['name']].strftime("%Y-%m-%d")
            add_log(tmp_user, item.id, '物品', template.key_name, '', name)
            add_log(tmp_user, item.id, '物品', template.custom_id_name, '', custom_id)
            set_extradata(item, template, data, tmp_user)
        else:
            return render(request, 'inventory/edit.html', locals())
        message = _("新建成功！")
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
            is_property = item.template.is_property
            for data in item.template.extra_data:
                filled = False
                if data['name'] in item_keys:
                    data_name = data['name']
                    item_keys.remove(data_name)
                    if data['type'] in ['int', 'float'
                                        ] or item.extra_data[data['name']]:
                        if data['type'] not in [
                                'bool', 'int', 'float', 'text', 'date'
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
                                    'data': '无权限或已删除',
                                    'type': 'warning',
                                }))
                            except ValueError:
                                extra_info.append((data_name, {
                                    'data': '数据未更新',
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
            relation_info[gettext('作为以下') +
                          key.replace('__', gettext('的'))] = get_my_list(
                              tmp_user, Item.objects.filter(id__in=values))
        del_permission = item.del_permission(tmp_user)
        unlink_permission = item.unlink_permission(tmp_user)
        return render(request, 'inventory/item.html', locals())

    def post(self, request, *args, **kwargs):
        item = self.item
        action = request.GET['action']
        if action == 'user':
            allowed_users_old = item.allowed_users_str()
            item.allowed_users.clear()
            item.allowed_users.add(item.owner)
            for user_id in request.POST.getlist('share'):
                item.allowed_users.add(myUser.objects.get(id=user_id))
            allowed_users_new = item.allowed_users_str()
            item.save()
            if allowed_users_old != allowed_users_new:
                add_log(self.tmp_user, item.id, '物品', '白名单', allowed_users_old,
                        allowed_users_new)
            self.message = _("保存成功！")
        return self.get(request, *args, **kwargs)


def template_ajax(request, *args, **kwargs):
    user_id = request.session.get('user_id')
    tmp_user = myUser.objects.get(id=user_id)
    template_id = int(request.POST.get('id', 0))
    if template_id != 0:
        template = ItemTemplate.objects.get(id=template_id)
        custom_id = replace_date(template.custom_id_format)

        if '%id%' in custom_id:
            tmp_id_max = tmp_id_min = 1  # Both tmp_id_max and tmp_id_min should be stabilize to old tmp_id

            # Binary Search with Auto Expand
            while Item.objects.filter(
                    custom_id=custom_id.replace('%id%', str(
                        tmp_id_max))).exists():
                tmp_id_max *= 2
            while tmp_id_min < tmp_id_max:
                tmp_id = (tmp_id_min + tmp_id_max) // 2
                if Item.objects.filter(
                    custom_id=custom_id.replace('%id%', str(
                        tmp_id))).exists():
                    tmp_id_min = tmp_id + 1
                else:
                    tmp_id_max = tmp_id

            # While Loop
            # while Item.objects.filter(
            #         custom_id=custom_id.replace('%id%', str(
            #             tmp_id_min))).exists():
            #     tmp_id_min += 1

            # Cached ID
            # if IdCache.objects.filter(pattern=custom_id).exists():
            #     IdCache.objects.create(pattern=custom_id)
            #     tmp_id_min = IdCache.objects.get(pattern=custom_id).next_id

            custom_id = custom_id.replace('%id%', str(tmp_id_min))
        edit_form = forms.EditItemForm(*args, template=template, user=tmp_user)
    return render(request, 'inventory/editajax.html', locals())


class EditItemView(generic.View):
    tmp_user = None
    item = None
    message = None

    def get(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        tmp_user = myUser.objects.get(id=user_id)
        item = get_my_item(tmp_user, kwargs.get('item_id'))
        template_id = item.template.id
        is_property = item.template.is_property
        is_edit = True
        name = "属性" if is_property else _("物品")
        action = "编辑"
        action_translated = _(action) + ' '
        if not item.del_permission(tmp_user):
            messages.error(request,
                           "只有创建人（{}）及其管理员可以编辑物品！".format(item.owner.name))
            return render(request, 'inventory/info.html', locals())
        template_queryset = get_my_template_queryset(
            tmp_user, ItemTemplate.objects.all())
        choose_form = forms.ChooseTemplateForm(
            is_property=is_property, template_queryset=template_queryset)
        add_form = forms.AddItemForm()
        return render(request, 'inventory/edit.html', locals())

    def post(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        item = get_my_item(tmp_user, kwargs.get('item_id'))
        is_property = item.template.is_property
        action = "编辑"
        action_translated = _(action) + ' '
        if not item.del_permission(tmp_user):
            messages.error(request,
                           "只有创建人（{}）及其管理员可以编辑物品！".format(item.owner.name))
            return render(request, 'inventory/info.html', locals())
        self.message = _("请检查填写的内容！")
        add_form = forms.AddItemForm(request.POST)
        if add_form.is_valid():
            name_old = item.name
            name_new = add_form.cleaned_data['name']
            is_public_old = item.is_public
            is_public_new = add_form.cleaned_data['public']
        else:
            return self.get(request, *args, **kwargs)
        template_queryset = get_my_template_queryset(
            tmp_user, ItemTemplate.objects.all())
        choose_form = forms.ChooseTemplateForm(
            request.POST, template_queryset=template_queryset)
        if choose_form.is_valid():
            data = {}
            template_id = int(choose_form.cleaned_data['template'])
            template = ItemTemplate.objects.get(id=template_id)
            edit_form = forms.EditItemForm(
                request.POST, template=template, user=tmp_user)
            if edit_form.is_valid():
                for dictionary in template.extra_data:
                    data[dictionary['name']] = edit_form.cleaned_data[
                        dictionary['name'].replace(' ', '_')]
                    if data[dictionary['name']]:
                        if dictionary['type'] == 'link':
                            data[dictionary['name']] = int(
                                data[dictionary['name']])
                        elif dictionary['type'] == 'date':
                            data[dictionary['name']] = data[
                                dictionary['name']].strftime("%Y-%m-%d")
        else:
            return self.get(request, *args, **kwargs)
        if 'save_as_new' in request.POST:
            new_item = Item.objects.create(
                name=name_new,
                location=None,
                owner=tmp_user,
                is_public=is_public_new,
            )
            add_log(tmp_user, new_item.id, '物品', template.key_name, '', name_new)
            add_log(tmp_user, new_item.id, '物品', '公开', 'False',
                    'True' if is_public_new else 'False')
            for user in item.allowed_users.all():
                new_item.allowed_users.add(user)
            add_log(tmp_user, new_item.id, '物品', '白名单', '',
                    new_item.allowed_users_str())
            set_extradata(new_item, template, data, tmp_user)
            new_item.save()
            return redirect('inventory:item', new_item.id)
        else:
            if name_old != name_new:
                add_log(tmp_user, item.id, '物品', template.key_name, name_old, name_new)
            if is_public_old != is_public_new:
                add_log(tmp_user, item.id, '物品', '公开',
                        'True' if is_public_old else 'False',
                        'True' if is_public_new else 'False')
            item.name = add_form.cleaned_data['name']
            item.is_public = add_form.cleaned_data['public']
            set_extradata(item, template, data, tmp_user)
            item.save()
            message = _("修改成功！")
            return redirect('inventory:item', item.id)


class TemplatesView(generic.View):
    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        template_list = ItemTemplate.objects.all()
        keyword = request.GET.get('q')
        if keyword:
            keyword_iri = quote(keyword)
            template_list = template_list.filter(name__contains=keyword)
        else:
            keyword = ''
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
        is_property = template.is_property
        export_keys = get_export_keys(template, include_links=False)
        all_objs = get_my_list(tmp_user,
                               Item.objects.filter(template=template))
        full_info = [
            get_export_values(
                template, obj, include_links=False, user=tmp_user)
            for obj in all_objs
        ]
        return render(request, 'inventory/template.html', locals())


class TemplateExportView(generic.View):
    def get(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        template = get_object_or_404(ItemTemplate, id=kwargs.get('id'))
        export_keys = get_export_keys(template)
        all_objs = get_my_list(tmp_user,
                               Item.objects.filter(template=template))
        full_info = [
            get_export_values(template, obj, user=tmp_user) for obj in all_objs
        ]
        return render(request, 'inventory/template_export.html', locals())


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
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        add_form = forms.AddTemplateForm(request.POST)
        message = _("请检查填写的内容！")
        if add_form.is_valid():
            name = add_form.cleaned_data['name']
            try:
                new_template = ItemTemplate.objects.create(
                    name=name,
                    key_name=_("名称"),
                    key_name_placeholder=_("用于显示的名称"),
                    custom_id_name=_("自定编号"),
                    is_property=request.GET.get('property') is not None,
                )
                new_template.save()
                message = _("新建成功！")
            except IntegrityError:
                message = _("模板名称重复！")
                return render(request, 'inventory/template_add.html', locals())
            category = "物品属性" if request.GET.get('property') else "物品"
            add_log(tmp_user, new_template.id, '模板', '名称', '', name)
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
        choices = ['text', 'bool', 'int', 'float', 'date']
        choices.extend([
            name[0] for name in ItemTemplate.objects.all().values_list('name')
        ])
        all_users = myUser.objects.all()
        return render(request, 'inventory/template_edit.html', locals())

    def post(self, request, *args, **kwargs):
        tmp_user = myUser.objects.get(id=request.session.get('user_id'))
        choices = ['text', 'bool', 'int', 'float', 'date']
        choices.extend([
            name[0] for name in ItemTemplate.objects.all().values_list('name')
        ])
        message = _("请检查填写的内容！")
        template = get_object_or_404(ItemTemplate, id=kwargs.get('id'))
        my_list = []
        idx_list = []
        key_name_new = request.POST.get('key_name', '名称')
        if template.key_name != key_name_new:
            add_log(tmp_user, template.id, '模板', '名称', template.key_name,
                    key_name_new)
            template.key_name = key_name_new
        key_name_placeholder_new = request.POST.get('key_name_placeholder',
                                                    '用于显示的名称')
        if template.key_name_placeholder != key_name_placeholder_new:
            add_log(tmp_user, template.id, '模板', '用于显示的名称',
                    template.key_name_placeholder, key_name_placeholder_new)
            template.key_name_placeholder = key_name_placeholder_new
        custom_id_name_new = request.POST.get('custom_id_name', '名称')
        if template.custom_id_name != custom_id_name_new:
            add_log(tmp_user, template.id, '模板', 'ID名称', template.custom_id_name,
                    custom_id_name_new)
            template.custom_id_name = custom_id_name_new
        custom_id_format_new = request.POST.get('custom_id_format', None)
        if template.custom_id_format != custom_id_format_new:
            add_log(tmp_user, template.id, '模板', '自定编号',
                    template.custom_id_format, custom_id_format_new)
            template.custom_id_format = custom_id_format_new
        allowed_users_old = template.allowed_users_str()
        template.allowed_users.clear()
        for user_id in request.POST.getlist('share'):
            template.allowed_users.add(myUser.objects.get(id=user_id))
        allowed_users_new = template.allowed_users_str()
        if allowed_users_old != allowed_users_new:
            add_log(tmp_user, template.id, '模板', '白名单', allowed_users_old,
                    allowed_users_new)
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
        extra_data_old = template.extra_data
        template.extra_data = my_list
        template.save()
        extra_data_new = template.extra_data
        if extra_data_old != extra_data_new:
            add_log(tmp_user, template.id, '模板', '扩展数据', extra_data_old,
                    extra_data_new)
        message = _("保存成功")
        return redirect('inventory:template', kwargs.get('id'))


def del_template(request, template_id):
    tmp_user = myUser.objects.get(id=request.session.get('user_id'))
    if not tmp_user.is_superadmin:
        raise Http404()
    template = get_object_or_404(ItemTemplate, id=template_id)
    template.delete()
    return redirect('inventory:templates')


def alt_template(request, template_id):
    tmp_user = myUser.objects.get(id=request.session.get('user_id'))
    if not tmp_user.is_superadmin:
        raise Http404()
    template = get_object_or_404(ItemTemplate, id=template_id)
    template.is_property = not template.is_property
    if template.is_property:
        add_log(tmp_user, template.id, '模板', '不可存入', 'False', 'True')
    else:
        add_log(tmp_user, template.id, '模板', '不可存入', 'True', 'False')
    template.save()
    return redirect('inventory:template', template_id)


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
                self.message = _("路径名称重复！")
                return self.get(request, *args, **kwargs)
            new_location = Location.objects.create(
                path=path,
                parent=loc_now,
                is_public=public,
            )
            new_location.save()
            add_log(tmp_user, new_location.id, '位置', '名称', '',
                    new_location.__str__())
            add_log(tmp_user, new_location.id, '位置', '公开', 'False',
                    'True' if public else 'False')
            self.message = _("新建成功！")
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
    for key, values in item.related_items.items():
        for value in values:
            ext_item = Item.objects.get(id=value)
            ext_item.extra_data[key.split('__')[1]] = 0
            ext_item.save()
    set_location(item, None, tmp_user)
    set_extradata(item, None, {}, tmp_user)
    item.delete()
    return redirect('inventory:properties') if is_property else redirect(
        'inventory:items')


def unlink_item(request, item_id):
    user_id = request.session.get('user_id')
    tmp_user = myUser.objects.get(id=user_id)
    item = get_my_item(tmp_user, item_id)
    allowed_users_old = item.allowed_users_str()
    if item.unlink_permission(tmp_user):
        messages.error(request, "您不能取消关联该物品！")
        return render(request, 'inventory/info.html', locals())
    item.allowed_users.remove(tmp_user)
    allowed_users_new = item.allowed_users_str()
    add_log(tmp_user, item.id, '物品', '白名单', allowed_users_old,
            allowed_users_new)
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
            message = _("请检查填写的内容！")
            if apply_form.is_valid():
                if LocationPermissionApplication.objects.filter(
                        applicant=tmp_user,
                        location=loc,
                        closed=False,
                ).exists():
                    message = _("请勿重复提交")
                    return render(request, 'inventory/location_apply.html',
                                  locals())
                else:
                    new_form = LocationPermissionApplication.objects.create(
                        applicant=tmp_user,
                        location=loc,
                        explanation=apply_form.cleaned_data['note'],
                    )
                    new_form.save()
                    message = _("提交成功")
                    return redirect('personal:mylocreq')
            else:
                return self.get(request)
        return redirect('inventory:location', loc_id)


def rebuild(request):
    rebuild_related()
    return redirect('inventory:index')
