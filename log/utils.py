from .models import Log


def add_log(user, obj_id, category, attribute, before, after):
    log = Log.objects.create(
        operator=user,
        obj_id=obj_id,
        category=category,
        attribute=attribute,
        before=before,
        after=after,
    )
    log.save()