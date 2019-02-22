from django import forms
from captcha.fields import CaptchaField
from django.utils.translation import gettext_lazy as _

class UserForm(forms.Form):
    username = forms.CharField(
        label=_("用户名"),
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        label=_("密码"),
        max_length=256,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    captcha = CaptchaField(label=_("验证码(点击图片更换)"))


class RegisterForm(forms.Form):
    username = forms.CharField(
        label=_("用户名"),
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(
        label=_("密码"),
        max_length=256,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(
        label=_("确认密码"),
        max_length=256,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(
        label=_("邮箱地址"), widget=forms.EmailInput(attrs={'class': 'form-control'}))
    captcha = CaptchaField(label=_("验证码(点击图片更换)"))
