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
    for item in template.extra_data:
        if item['type'] in ['text', 'int', 'float', 'bool'] or not include_links:
            keys.append(item['name'])
        elif include_links:
            inner_template = ItemTemplate.objects.get(name=item['type'])
            for name in get_export_keys(inner_template, visited.copy(), inner_template not in visited):
                keys.append(item['name']+'__'+name)
    return keys
