import time

from django.utils.deprecation import MiddlewareMixin
from traffic.models import Traffic
from login.models import User


class Profiler(MiddlewareMixin):
    def __call__(self, request):
        t_start = time.clock() * 1000
        response = self.get_response(request)
        duration = time.clock() * 1000 - t_start
        tmp_user = User.objects.get(id=request.session.get('user_id'))
        if 'HTTP_X_FORWARDED_FOR' in request.META.keys():
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        traffic = Traffic.objects.create(
            url=request.path_info,
            user=tmp_user,
            ip=ip,
            http_status=response.status_code,
            response_time=duration,
        )
        traffic.save()
        return response
