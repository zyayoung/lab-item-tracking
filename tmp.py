from inventory.models import LocationPermissionApplication

for req in LocationPermissionApplication.objects.all():
    if req.rejected or req.approved:
        req.closed = True
        req.save()
