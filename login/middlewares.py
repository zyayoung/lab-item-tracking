import re

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect, HttpResponse, render


class AuthMD(MiddlewareMixin):
    reg_list = [
        r"^/$",
        r"^/login/$",
        r"^/register/$",
        r"^/captcha/.*",
        r"^/confirm/",
        r"^/admin/.*",
    ]

    def process_request(self, request):
        request_url = request.path_info
        reg_str = "|".join(r"(" + reg_ex + r")" for reg_ex in self.reg_list)
        if request.session.get('is_login') or re.match(reg_str, request_url):
            return
        else:
            return render(request, 'inventory/index.html')
