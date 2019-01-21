import re

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect, HttpResponse, render

class AuthMD(MiddlewareMixin):
    reg_ex = r"(^/login/$)|(^/register/$)|(^/captcha/.*)"

    def process_request(self, request):
        request_url = request.path_info
        # print(request.path_info, request.get_full_path())
        if re.match(self.reg_ex, request_url) or request.session.get('is_login'):
            return
        else:
            return render(request, 'inventory/index.html')