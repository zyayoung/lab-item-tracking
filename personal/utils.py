from inventory.models import LocationPermissionApplication as LocPmsnApp


def get_my_request_list(user_now):
    all_obj = LocPmsnApp.objects.all()
    obj_list = all_obj.filter(applicant=user_now)
    return obj_list.distinct()


def get_others_request_list(user_now):
    all_obj = LocPmsnApp.objects.all()
    obj_list = all_obj.filter(auditor=user_now)
    users = user_now.staff.all()
    for user in users:
        obj_list = obj_list | all_obj.filter(applicant=user)
    return obj_list.distinct()