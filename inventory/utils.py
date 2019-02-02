from django.shortcuts import get_object_or_404
from django.http import Http404
from inventory.models import Item, Location, ItemTemplate
from trace_item.models import ItemLog


def get_my_item(user_now, item_id):
    item = get_object_or_404(Item, id=item_id)
    # two cases: (admin) and (not admin)
    if not (item.is_public or
            user_now.is_superadmin or
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
            location_from=item.location,
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
            for key in get_export_keys(inner_template, visited.copy(), inner_template not in visited):
                keys.append(ext_data['name']+'__'+key)
    return keys


def get_export_values(template, item, visited=[], include_links=True):
    visited.append(template)
    keys = [item.name if item else '']
    for ext_data in template.extra_data:
        int_data = item.extra_data[ext_data['name']] if item and ext_data['name'] in item.extra_data.keys() else ''
        if ext_data['type'] not in ['text', 'int', 'float', 'bool'] and not include_links:
            if item and int_data != "0":
                keys.append(Item.objects.get(id=int_data).name)
            else:
                keys.append('')
        elif ext_data['type'] in ['text', 'int', 'float', 'bool'] or not include_links:
            keys.append(int_data)
        elif include_links:
            inner_template = ItemTemplate.objects.get(name=ext_data['type'])
            try:
                inner_item = Item.objects.get(id=int_data) if int_data else None
            except Item.DoesNotExist:
                inner_item = None
            for value in get_export_values(inner_template, inner_item, visited.copy(), inner_template not in visited):
                keys.append(value)
    return keys
