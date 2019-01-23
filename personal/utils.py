from inventory.models import LocationPermissionApplication as LocPmsnApp
from inventory.models import Location
from inventory.utils import get_my_list
from silk.profiling.profiler import silk_profile


def get_my_request_list(user_now):
    all_obj = LocPmsnApp.objects.all()
    obj_list = all_obj.filter(applicant=user_now)
    return obj_list.distinct()


def get_others_request_list(user_now):
    all_obj = LocPmsnApp.objects.all()
    if user_now.is_superadmin:
        return all_obj
    loc_list = get_my_list(user_now, Location.objects.all())
    users = user_now.staff.all()
    obj_list = all_obj.filter(location__in=loc_list, applicant__in=users)
    return obj_list.distinct()
