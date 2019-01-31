from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from . import models
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from . import forms
from django.conf import settings
import hashlib
import datetime
from urllib import request, parse

# Create your views here.


def hash_code(password, salt='addsomesalt'):
    h = hashlib.sha256()
    password += salt
    h.update(password.encode())
    return h.hexdigest()


def index(request):
    return render(request, 'login/index.html')


def login(request):
    if request.session.get('is_login', None):
        return redirect("/index/")
    hashkey = CaptchaStore.generate_key()
    image_url = captcha_image_url(hashkey)
    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if settings.EMAIL_ENABLE and not user.has_confirmed:
                    message = "该用户还未通过邮件确认！"
                    return render(request, 'login/login.html', locals())
                if user.password == hash_code(password):
                    request.session['is_login'] = True
                    request.session['is_superadmin'] = user.is_superadmin
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.__str__()
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        return render(request, 'login/login.html', locals())

    login_form = forms.UserForm()
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        return redirect("/index/")
    hashkey = CaptchaStore.generate_key()
    image_url = captcha_image_url(hashkey)
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            if password1 != password2:
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'login/register.html', locals())

            # 当一切都OK的情况下，创建新用户
            new_user = models.User.objects.create()
            new_user.name = username
            new_user.password = hash_code(password1)
            new_user.email = email
            new_user.save()
            if settings.EMAIL_ENABLE:
                # Send confirm email
                code = get_confirm_string(new_user)
                send_email(email, code)
            message = "请前往注册邮箱，进行邮件确认！"
            return render(request, 'login/confirm.html', locals())
            # return redirect('/login/')
        else:
            if request.POST.get('captcha_1') == "":
                message = "验证码不能为空"
    register_form = forms.RegisterForm()
    return render(request, 'login/register.html', locals())


def send_email(email, code):
    from django.core.mail import EmailMultiAlternatives
    subject = '验证您的注册邮箱'
    text_content = '''请在浏览器中访问以下地址完成注册确认！\
                    http://{0}/confirm/?code={1}\
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！
                    '''.format(settings.SITE_DOMAIN, code)
    html_content = '''<p>请点击以下链接完成注册确认！</p>
                    <p><a href="http://{0}/confirm/?code={1}" target=blank>http://{0}/confirm/?code={1}</a></p>
                    <p>此链接有效期为{2}天！</p>
                    '''.format(settings.SITE_DOMAIN, code,
                               settings.CONFIRM_DAYS)
    try:
        url = settings.EMAIL_API + '?to=' + parse.quote(email) + '&title=' + parse.quote(subject) + '&body=' + parse.quote(text_content) + '&html=' + parse.quote(html_content)
        print(url)
        request.urlopen(url)
    except:
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            settings.EMAIL_HOST_USER,
            [email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()


def get_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(user.name, now)
    models.ConfirmString.objects.create(
        code=code,
        user=user,
    )
    return code


def logout(request):
    if not request.session.get('is_login', None):
        return redirect("/index/")
    # request.session.flush()
    del request.session['is_login']
    del request.session['is_superadmin']
    del request.session['user_id']
    del request.session['user_name']
    return redirect("/index/")


def user_confirm(request):
    code = request.GET.get('code')
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求!'
        return render(request, 'login/confirm.html', locals())
    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已经过期！请重新注册!'
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
    return render(request, 'login/confirm.html', locals())
