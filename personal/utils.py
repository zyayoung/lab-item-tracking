from inventory.models import LocationPermissionApplication as LocPmsnApp


def get_request_list(user_now):
    all_obj = LocPmsnApp.objects.all()
    obj_list = all_obj.filter(applicant=user_now) | all_obj.filter(
        auditor=user_now)
    users = user_now.staff.all()
    for user in users:
        obj_list = obj_list | all_obj.filter(applicant=user) | all_obj.filter(
        auditor=user)
    return obj_list.distinct()