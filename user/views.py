import string
import random
import time
from django.shortcuts import redirect,reverse
from django.shortcuts import render
from django.contrib import  auth
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.mail import send_mail
from .forms import LoginForm,RegForm,ChangeNicknameForm,BindEmailForm,ChangePasswordForm,ForgotPasswordForm
from .models import Profile

# Create your views here.
def login_for_modal(request):
    login_form = LoginForm(request.POST)
    data = {}
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request,user)
            return redirect(request.GET.get('from',reverse('home')))
    else:
        login_form = LoginForm()

    context = {}
    context['login_form'] = login_form
    return render(request, 'user/login.html', context)

def register(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST,request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            user = User.objects.create_user(username=username,email=email,password=password)
            user.save()

            del request.session['register_code']

            user = auth.authenticate(username=username,password=password)
            auth.login(request,user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        reg_form = RegForm()

    context = {}
    context['reg_form'] = reg_form
    return render(request, 'user/register.html', context)

def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))

def user_info(request):
    context = {}
    return render(request, 'user/user_info.html', context)

def change_nickname(request):
    redirect_to = request.GET.get('from',reverse('home'))
    if not request.user.is_authenticated:
        return redirect(reverse('home'))
    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST,user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['nickname_new']
            profile,created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()

    context = {}
    context['page_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '修改'
    context['return_back_url'] = redirect_to
    context['form'] = form
    return render(request,'form.html',context)

def bind_email(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if not request.user.is_authenticated:
        return redirect(reverse('home'))
    if request.method == 'POST':
        form = BindEmailForm(request.POST,request=request)
        if form.is_valid():
            email = form.cleaned_data['email_new']
            request.user.email = email
            request.user.save()

            del request.session['bind_email_code']

            return redirect(redirect_to)
    else:
        form = BindEmailForm()

    context = {}
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_text'] = '绑定'
    context['return_back_url'] = redirect_to
    context['form'] = form
    return render(request, 'user/bind_email.html', context)

def send_verification_code(request):
    email = request.GET.get('email','')
    send_for = request.GET.get('send_for', '')
    email_tile = request.GET.get('email_tile', '邮箱标题')
    print(email_tile)
    data = {}
    if email != '':
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits,4))
        now = int(time.time())
        send_code_time = request.session.get('send_code_time',0)
        if now - send_code_time < 60:
            data['status'] = 'ERROR_CODE_TIME'
            data['time'] = now - send_code_time
        else:
            request.session[send_for] = code
            request.session['send_code_time'] = now
            # 发送邮件
            send_mail(
                email_tile,
                '验证码：%s' % code,
                '522062785@qq.com',
                [email],
                fail_silently=False,
            )

            data['status'] = 'SUCCESS'

    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

def change_password(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if not request.user.is_authenticated:
        return redirect(reverse('home'))
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            request.user.set_password(new_password)
            request.user.save()
            auth.logout(request)
            return redirect(reverse('home'))
    else:
        form = ChangePasswordForm()

    context = {}
    context['page_title'] = '修改密码'
    context['form_title'] = '修改密码'
    context['submit_text'] = '修改'
    context['return_back_url'] = redirect_to
    context['form'] = form
    return render(request, 'form.html', context)

def forgot_password(request):
    redirect_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            return redirect(reverse('home'))
    else:
        form = ForgotPasswordForm()

    context = {}
    context['page_title'] = '重置密码'
    context['form_title'] = '重置密码'
    context['submit_text'] = '修改'
    context['return_back_url'] = redirect_to
    context['form'] = form
    return render(request, 'user/forgot_pwd.html', context)