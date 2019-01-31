from django.shortcuts import redirect


def check_admin(func):
    def inner(*args, **kwargs):
        try:
            request = args[1]
        except IndexError:
            request = args[0]
        if not request.session.get('is_superadmin', False):
            return redirect('inventory:index')
        return func(*args, **kwargs)

    return inner
