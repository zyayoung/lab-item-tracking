from django.shortcuts import get_object_or_404
from django.http import Http404
from inventory.models import Item, Location
from trace_item.models import ItemLog
from silk.profiling.profiler import silk_profile


@silk_profile(name='get_my_item')
def get_my_item(user_now, item_id):
    item = get_object_or_404(Item, id=item_id)
    # two cases: (admin) and (not admin)
    if not (item.is_public or
            user_now.is_superadmin or
            (user_now.staff.all() & item.allowed_users.all()).exists() or
            (item.allowed_users.filter(id=user_now.id).exists())):
        raise Http404()
    return item


@silk_profile(name='get_my_loc')
def get_my_loc(user_now, loc_id):
    loc = get_object_or_404(Location, id=loc_id)
    # two cases: (admin) and (not admin)
    if not (loc.is_public or
            user_now.is_superadmin or
            (user_now.staff.all() & loc.allowed_users.all()).exists() or
            (loc.allowed_users.filter(id=user_now.id).exists())):
        raise Http404()
    return loc


@silk_profile(name='get_my_list')
def get_my_list(user_now, all_obj):
    if user_now.is_superadmin:
        return all_obj
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
            quantity_from=item.quantity,
            quantity_to=item.quantity,
        )
        log.save()
        item.location = location
        item.save()


def set_quantity(item, quantity, user):
    if quantity != item.quantity:
        log = ItemLog.objects.create(
            item=item,
            operator=user,
            location_from=item.location,
            location_to=item.location,
            quantity_from=item.quantity,
            quantity_to=quantity,
        )
        log.save()
        item.quantity = quantity
        item.save()
