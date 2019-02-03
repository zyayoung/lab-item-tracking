from django.shortcuts import get_object_or_404
from django.http import Http404
from inventory.models import Item, Location, ItemTemplate
from trace_item.models import ItemLog


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
    if not (loc.is_public or
            user_now.is_superadmin or
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


def set_location(item, location, user):
    if location != item.location:
        log = ItemLog.objects.create(
            item=item,
            operator=user,
            location_to=location,
        )
        log.save()
        item.location = location
        item.save()


def get_export_keys(template, visited=[], include_links=True):
    visited.append(template)
    keys = [template.key_name]
    for ext_data in template.extra_data:
        if ext_data['type'] in ['text', 'int', 'float', 'bool'] or not include_links:
            keys.append(ext_data['name'])
        elif include_links:
            inner_template = ItemTemplate.objects.get(name=ext_data['type'])
            for key in get_export_keys(inner_template, visited, inner_template not in visited):
                keys.append(ext_data['name']+'__'+key)
    visited.pop()
    if not template.is_property:
        keys.append('位置')
    return keys


def get_export_values(template, item, visited=[], include_links=True, user=None):
    visited.append(template)
    keys = [item.name if item else '']
    for ext_data in template.extra_data:
        int_data = item.extra_data[ext_data['name']] if item and ext_data['name'] in item.extra_data.keys() else ''
        if ext_data['type'] in ['text', 'int', 'float', 'bool']:
            keys.append(int_data)
        elif include_links:
            inner_template = ItemTemplate.objects.get(name=ext_data['type'])
            try:
                inner_item = get_my_item(user, int_data) if int_data else None
            except Http404:
                inner_item = None
            for value in get_export_values(inner_template, inner_item, visited, inner_template not in visited):
                keys.append(value)
        else:
            try:
                keys.append(get_my_item(user, int_data) if int_data else '')
            except Http404:
                keys.append('')
    if not template.is_property:
        loc = item.location if item else ''
        keys.append(loc if loc else '')
    visited.pop()
    return keys


def set_extradata(item, template, extra_data, user):
    if item.extra_data == extra_data:
        return
    log = ItemLog.objects.create(
        item=item,
        operator=user,
        extra_data_to=extra_data,
    )
    log.save()

    # unlink old relationships
    if item.template:
        item_keys = item.extra_data.keys()
        for data in item.template.extra_data:
            if data['name'] in item_keys:
                data_name = data['name']
                if item.extra_data[data['name']] and \
                    data['type'] not in ['bool', 'int', 'float', 'text']:
                    if int(item.extra_data[data_name]) != 0:
                        ext_item = get_object_or_404(Item, id=item.extra_data[data_name])
                        if item.template.name+'__'+data['name'] in ext_item.related_items.keys():
                            related_info = ext_item.related_items[item.template.name+'__'+data['name']]
                            if item.id in related_info:
                                related_info.remove(item.id)
                        else:
                            related_info = []
                        if ext_item == item:
                            item.related_items[item.template.name + '__' + data['name']] = related_info
                            item.save()
                        else:
                            ext_item.related_items[item.template.name + '__' + data['name']] = related_info
                            ext_item.save()

    # link new relationships
    if template:
        item_keys = extra_data.keys()
        for data in template.extra_data:
            if data['name'] in item_keys:
                data_name = data['name']
                if extra_data[data['name']] and \
                    data['type'] not in ['bool', 'int', 'float', 'text']:
                    if int(extra_data[data_name]) != 0:
                        ext_item = get_object_or_404(Item, id=extra_data[data_name])
                        if template.name+'__'+data['name'] in ext_item.related_items.keys():
                            related_info = ext_item.related_items[template.name+'__'+data['name']]
                            related_info.append(item.id)
                        else:
                            related_info = [item.id]
                        if ext_item == item:
                            item.related_items[template.name + '__' + data['name']] = related_info
                            item.save()
                        else:
                            ext_item.related_items[template.name + '__' + data['name']] = related_info
                            ext_item.save()
    item.extra_data = extra_data
    item.template = template
    item.save()


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
                    data['type'] not in ['bool', 'int', 'float', 'text']:
                    if int(extra_data[data_name]) != 0:
                        ext_item = get_object_or_404(Item, id=item.extra_data[data_name])
                        if template.name+'__'+data['name'] in ext_item.related_items.keys():
                            related_info = ext_item.related_items[template.name+'__'+data['name']]
                            related_info.append(item.id)
                        else:
                            related_info = [item.id]
                        if ext_item == item:
                            item.related_items[template.name + '__' + data['name']] = related_info
                            item.save()
                        else:
                            ext_item.related_items[template.name + '__' + data['name']] = related_info
                            ext_item.save()
