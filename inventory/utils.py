from django.shortcuts import get_object_or_404, resolve_url
from django.http import Http404
from inventory.models import Item, Location, ItemTemplate
from login.models import User as myUser
from trace_item.models import ItemLog
from log.utils import *


def get_my_user(user_now, user_id):
    user = get_object_or_404(myUser, id=user_id)
    if not user_now or user_now.is_superadmin or user == user_now:
        return user
    if not user in user_now.staff.all():
        raise Http404()
    return user

def get_my_item(user_now, item_id):
    item = get_object_or_404(Item, id=item_id)
    if not user_now or user_now.is_superadmin:
        return item
    # two cases: (admin) and (not admin)
    if not (item.is_public or
            (user_now.staff.all() & item.allowed_users.all()).exists() or
            (item.allowed_users.filter(id=user_now.id).exists())):
        raise Http404()
    return item


def get_my_loc(user_now, loc_id):
    loc = get_object_or_404(Location, id=loc_id)
    # two cases: (admin) and (not admin)
    if not (loc.is_public or user_now.is_superadmin or
            (user_now.staff.all() & loc.allowed_users.all()).exists() or
            (loc.allowed_users.filter(id=user_now.id).exists())):
        raise Http404()
    return loc


def get_my_list(user_now, all_obj):
    if user_now.is_superadmin:
        return all_obj.filter()
    users = user_now.staff.all()
    obj_list = all_obj.filter(allowed_users=user_now) | \
        all_obj.filter(is_public=True) | \
        all_obj.filter(allowed_users__in=users)
    return obj_list.distinct()


def get_my_template_queryset(user_now, all_obj):
    if user_now.is_superadmin:
        return all_obj.filter()
    users = user_now.staff.all()
    obj_list = all_obj.filter(allowed_users=user_now) | \
        all_obj.filter(allowed_users=None) | \
        all_obj.filter(allowed_users__in=users)
    return obj_list.distinct()


def set_location(item, location, user):
    if location != item.location:
        log = ItemLog.objects.create(
            item=item,
            operator=user,
            location_from=item.location,
            location_to=location,
        )
        old_loc = item.location.__str__()
        item.location = location
        item.save()
        add_log(user, item.id, '物品', '位置', old_loc, location.__str__())


def get_export_keys(template, visited=[], include_links=True):
    visited.append(template)
    keys = [template.key_name]
    for ext_data in template.extra_data:
        if ext_data['type'] in ['bool', 'int', 'float', 'text', 'date'
                                ] or not include_links:
            keys.append(ext_data['name'])
        elif include_links:
            try:
                inner_template = ItemTemplate.objects.get(
                    name=ext_data['type'])
                for key in get_export_keys(inner_template, visited,
                                           inner_template not in visited):
                    keys.append(ext_data['name'] + '__' + key)
            except ItemTemplate.DoesNotExist:
                continue
    visited.pop()
    if not template.is_property:
        keys.append('位置')
    keys.append('创建者')
    return keys


def get_export_values(template,
                      item,
                      visited=[],
                      include_links=True,
                      user=None):
    visited.append(template)
    keys = [{
        'name': item.name if item else '',
        'href': resolve_url('inventory:item', item.id) if item else '',
    }]
    for ext_data in template.extra_data:
        int_data = item.extra_data[ext_data['name']] if item and ext_data[
            'name'] in item.extra_data.keys() else ''
        if ext_data['type'] in ['bool', 'int', 'float', 'text', 'date']:
            keys.append({
                'name': int_data if int_data else '',
                'href': '',
            })
        elif include_links:
            try:
                inner_template = ItemTemplate.objects.get(
                    name=ext_data['type'])
                try:
                    inner_item = get_my_item(user,
                                             int_data) if int_data else None
                except Http404:
                    inner_item = None
                except ValueError:
                    inner_item = None
                for value in get_export_values(inner_template, inner_item,
                                               visited,
                                               inner_template not in visited):
                    keys.append(value)
            except ItemTemplate.DoesNotExist:
                continue
        else:
            try:
                inner_item = get_my_item(user, int_data)
            except Http404:
                inner_item = None
            except ValueError:
                inner_item = None
            keys.append({
                'name': inner_item.name if inner_item else '',
                'href': resolve_url('inventory:item', inner_item.id) if inner_item else '',
            })
    if not template.is_property:
        loc = item.location if item else ''
        keys.append({
            'name': loc if loc else '',
            'href': resolve_url('inventory:location', loc.id) if loc else '',
        })
    keys.append({
        'name': item.owner if item else '',
        'href': resolve_url('personal:user', item.owner.id) if item else '',
    })
    visited.pop()
    return keys


def set_extradata(item, template, extra_data, user):
    log = ItemLog.objects.create(
        item=item,
        operator=user,
        extra_data_to=extra_data,
    )
    log.save()
    if item.template != template:
        add_log(user, item.id, '物品', '模板', item.template.__str__(),
                template.__str__())
    extra_data_old = '{}'
    extra_data_new = '{}'
    # unlink old relationships
    if item.template:
        extra_data_old = item.extra_data
        item_keys = item.extra_data.keys()
        for data in item.template.extra_data:
            if data['name'] in item_keys:
                data_name = data['name']
                if item.extra_data[data['name']] and \
                    data['type'] not in ['bool', 'int', 'float', 'text', 'date']:
                    try:
                        int(item.extra_data[data_name])
                    except ValueError:
                        continue
                    if int(item.extra_data[data_name]) != 0:
                        try:
                            ext_item = get_object_or_404(
                                Item, id=item.extra_data[data_name])
                            if item.template.name + '__' + data[
                                    'name'] in ext_item.related_items.keys():
                                related_info = ext_item.related_items[
                                    item.template.name + '__' + data['name']]
                                if item.id in related_info:
                                    related_info.remove(item.id)
                            else:
                                related_info = []
                            if ext_item == item:
                                item.related_items[item.template.name + '__' +
                                                   data['name']] = related_info
                                item.save()
                            else:
                                ext_item.related_items[
                                    item.template.name + '__' +
                                    data['name']] = related_info
                                ext_item.save()
                        except Http404:
                            pass

    # link new relationships
    if template:
        extra_data_new = extra_data
        item_keys = extra_data.keys()
        for data in template.extra_data:
            if data['name'] in item_keys:
                data_name = data['name']
                if extra_data[data['name']] and \
                    data['type'] not in ['bool', 'int', 'float', 'text', 'date']:
                    if int(extra_data[data_name]) != 0:
                        try:
                            ext_item = get_object_or_404(
                                Item, id=extra_data[data_name])
                            if template.name + '__' + data[
                                    'name'] in ext_item.related_items.keys():
                                related_info = ext_item.related_items[
                                    template.name + '__' + data['name']]
                                related_info.append(item.id)
                            else:
                                related_info = [item.id]
                            if ext_item == item:
                                item.related_items[template.name + '__' +
                                                   data['name']] = related_info
                                item.save()
                            else:
                                ext_item.related_items[
                                    template.name + '__' +
                                    data['name']] = related_info
                                ext_item.save()
                        except Http404:
                            pass
    item.extra_data = extra_data
    item.template = template
    item.save()
    if extra_data_old != extra_data_new:
        add_log(user, item.id, '物品', '属性', extra_data_old, extra_data_new)


def rebuild_related():
    # unlink old relationships
    for item in Item.objects.all():
        item.related_items = {}
        item.save()

    # link new relationships
    for item in Item.objects.all():
        if not item.template:
            continue
        template = item.template
        extra_data = item.extra_data
        item_keys = extra_data.keys()
        for data in template.extra_data:
            if data['name'] in item_keys:
                data_name = data['name']
                if extra_data[data['name']] and \
                    data['type'] not in ['bool', 'int', 'float', 'text', 'date']:
                    try:
                        int(item.extra_data[data_name])
                    except ValueError:
                        continue
                    if int(extra_data[data_name]) != 0:
                        ext_item = get_object_or_404(
                            Item, id=item.extra_data[data_name])
                        if template.name + '__' + data[
                                'name'] in ext_item.related_items.keys():
                            related_info = ext_item.related_items[
                                template.name + '__' + data['name']]
                            related_info.append(item.id)
                        else:
                            related_info = [item.id]
                        if ext_item == item:
                            item.related_items[template.name + '__' +
                                               data['name']] = related_info
                            item.save()
                        else:
                            ext_item.related_items[template.name + '__' +
                                                   data['name']] = related_info
                            ext_item.save()
