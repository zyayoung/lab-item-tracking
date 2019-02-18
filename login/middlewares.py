import re

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect, HttpResponse, render
from lab_item_tracking.urls import SSL_CERTIFICATION_URL


class AuthMD(MiddlewareMixin):
    reg_list = [
        r"^$",
        r"^index/$",
        r"^static/",
        r"^login/$",
        r"^register/$",
        r"^captcha/.*",
        r"^confirm/",
        r"^personal/settings/",
        r"^i18n/.*",
        r"^admin/.*",
        SSL_CERTIFICATION_URL,
    ]

    def process_request(self, request):
        request_url = request.path_info
        if request_url[0] == "/":
            request_url = request_url[1:]
        reg_str = "|".join(r"(" + reg_ex + r")" for reg_ex in self.reg_list)
        if request.session.get('is_login') or re.match(reg_str, request_url):
            return
        else:
            return redirect('inventory:index')
