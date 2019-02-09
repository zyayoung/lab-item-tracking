from .models import Log


def add_log(user, id, category, attribute, before, after):
    log = Log.objects.create(
        operator=user,
        _id=id,
        category=category,
        attribute=attribute,
        _from=before,
        _to=after,
    )
    log.save()