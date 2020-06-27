import os, logging
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse, QueryDict
from django.shortcuts import render, redirect
from django.urls import reverse
from users.models import Users
from utils.libs import random_base32, gen_qrcode, generate_otp
from NLP.settings import NO_VERFIY, BASE_DIR

logger_root = logging.getLogger(__name__)


def login(request):
    if request.method == 'GET':
        return render(request, 'users/login.html')
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        client_opt_code = request.POST.get('opt_code', '')
        if not all([username, password]):
            return render(request, 'users/login.html', {'error': '用户名/密码不能为空,请检查重新输入!'})
        user = authenticate(request=request, username=username, password=password)
        if not user:
            return render(request, 'users/login.html', {'error': '用户名/密码不能为空,请检查重新输入!'})
        is_login = False
        if NO_VERFIY:
            # 测试不校验验证码
            is_login = True
        else:
            if user.is_binding:
                sever_opt_code = generate_otp(user.secret_key)
                if sever_opt_code == client_opt_code:
                    is_login = True
            else:
                qrcode_url = user.qrcode_url
                username = user.username
                context = {'qrcode_url': qrcode_url, 'username': username}
                return render(request, 'users/qrcode.html', context=context)
        if is_login:
            django_login(request, user)
            request.session.set_expiry(0)
            return redirect(reverse('index'))
        else:
            return render(request, 'users/login.html', {"error": "验证码错误,请检查重新输入"})


# 校验是否绑定二维码和验证码是否校验通过
def verify_code(request):
    if request.method == "POST":
        username = request.POST.get('username', '')
        client_opt_code = request.POST.get('opt_code', '')
        user = Users.objects.get(username=username)
        secret_key = user.secret_key
        sever_opt_code = generate_otp(secret_key)
        if client_opt_code.isdigit() and all([username]):
            if client_opt_code == sever_opt_code:
                user.is_binding = True
                user.save()
                my_file = user.qrcode_url
                if os.path.exists(BASE_DIR + my_file):
                    os.remove(BASE_DIR + my_file)
                django_login(request, user)
                request.session.set_expiry(0)
                return redirect(reverse('index'))
            else:
                qrcode_url = user.qrcode_url
                context = {"error": "验证码不正确，请重新输入", 'qrcode_url': qrcode_url, 'username': username}
                return render(request, 'users/qrcode.html', context=context)
        else:
            qrcode_url = user.qrcode_url
            context = {"error": "验证码不正确，请重新输入", 'qrcode_url': qrcode_url, 'username': username}
            return render(request, 'users/qrcode.html', context=context)


def users(request):
    if request.method == 'GET':
        user_list = Users.objects.all().order_by("-id")
        # 获取 chat_id
        for user in user_list:
            try:
                obj_Potato = PotatoUserInfo.objects.get(username=user.potato_username)
            except:
                user.chat_id = ''
            else:
                user.chat_id = obj_Potato.chat_id
        context = {'users': user_list}
        return render(request, 'login/index.html', context=context)

    # 添加新用户
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        check_password = request.POST.get('check_password', '')
        if not all([username, password, check_password]):
            return JsonResponse({"code": 500, "msg": "参数有误，请重新输入"})
        user_queryset = Users.objects.filter(username=username)
        if len(user_queryset) == 0:
            if password == check_password:
                secret_key = random_base32()
                Users.objects.create(
                    username=username,
                    password=password,
                    secret_key=secret_key,
                    qrcode_url=gen_qrcode(username, secret_key)
                )
                return JsonResponse({"code": 200, "data": 'ok'})
            else:
                return JsonResponse({"code": 400, "msg": '两次输入密码不一致'})
        else:
            return JsonResponse({"code": 400, "msg": '用户已存在请重新输入'})

    # 删除所选用户
    if request.method == 'DELETE':
        username_list = list()
        delete = QueryDict(request.body)
        url_list = delete.getlist('data', None)
        if isinstance(url_list, list):
            for url in url_list:
                id_list = url.split('/')
                id = id_list[3]
                userObj = Users.objects.get(pk=id)
                username = userObj.username
                username_list.append(username)
                userObj.delete()
            comment = "{}用户删除{}用户成功".format(request.user, username_list)
            query_dict = {"username": username_list}
            recording_log(request, query_dict, comment)
            return JsonResponse({"code": 200, "data": "ok"})
        else:
            return JsonResponse({"code": 500, "data": "获取参数数据类型有误！！！"})


# 用户权限管理功能
def edit_users(request, user_id):
    # 展示用户管理详情页
    if request.method == "GET":
        if all([user_id]):
            user = Users.objects.get(pk=user_id)
            permission_config = PERMISSION_CONFIG
            permission_str = user.permission
            permission = permission_str.split(',')
            return render(request, 'login/permission.html', locals())
        else:
            return render(request, "404.html")

    # 实现修改用户权限，重置用户二维码功能
    if request.method == "POST":
        try:
            user = Users.objects.get(pk=user_id)
        except Users.DoesNotExist:
            return JsonResponse({"code": 500, "msg": "用户不存在！！！"})
        new_permission = request.POST.getlist('new_permission', None)
        tag = request.POST.get('tag', '')
        comment = ''
        if isinstance(new_permission, list) and all([tag]):
            new_permission = ",".join(new_permission)
            if new_permission == '':
                new_permission = '普通用户'
            if tag == "new_qrcode":
                user.is_binding = 0
                secret_key = random_base32()
                user.secret_key = secret_key
                user.qrcode_url = gen_qrcode(user.username, secret_key)
            if tag == "old_qrcode" and new_permission != user.permission:
                comment = "{}用户将{}用户权限修改为{}".format(request.user, user.username, new_permission)
            if tag == "new_qrcode" and new_permission != user.permission:
                comment = "{}用户重置{}用户二维码并且权限修改为{}".format(request.user, user.username, new_permission)
            if tag == "new_qrcode" and new_permission == user.permission:
                comment = '{}用户重置{}用户二维码成功'
            query_dict = {"tag": tag, "new_permission": new_permission, "old_permission": user.permission}
            recording_log(request, query_dict, comment)
            user.permission = new_permission
            user.save()
            return JsonResponse({"code": 200, "msg": "ok"})
        else:
            return JsonResponse({"code": 500, "msg": "获取参数异常！！"})


# 退出登陆
def logout(request):
    if request.method == "GET":
        django_logout(request)
        return redirect(reverse('users:login'))


# 用户修改自己的密码
def change_password(request):
    if request.method == "POST":
        user = request.user
        old_password = request.POST.get("old_password", '')
        new_password = request.POST.get("new_password", '')
        check_password = request.POST.get("check_password", '')
        if all([old_password, new_password, check_password]):
            if new_password != check_password:
                return JsonResponse({"code": 400, 'msg': "两次密码不一致，请重新输入"})
            if old_password == new_password:
                return JsonResponse({"code": 400, 'msg': "旧密码与新密码一致，请重新输入"})
            user.password = new_password
            user.save()
            query_dict = {"old_password": old_password, "new_password": new_password, "check_password": check_password}
            comment = "{}用户修改密码成功"
            recording_log(request, query_dict, comment)
            django_logout(request)
            return JsonResponse({"code": 200, 'msg': "ok"})
        else:
            return JsonResponse({"code": 500, 'msg': "参数有误，请检查参数！！"})


# 个人用户详情页
def user_setting(request):
    if request.method == "GET":
        user = request.user
        permission_str = user.permission
        permission = permission_str.split(',')
        # 获取 chat_id
        try:
            obj_Potato = PotatoUserInfo.objects.get(username=user.potato_username)
        except:
            user.chat_id = ''
        else:
            user.chat_id = obj_Potato.chat_id
        context = {"permission": permission, "permission_config": PERMISSION_CONFIG, "permission_str": permission_str}
        return render(request, 'login/personal_setting.html', context=context)


# 由管理员给用户重置密码
def update_password(request, user_id):
    if request.method == "POST":
        try:
            user = Users.objects.get(pk=user_id)
        except Users.DoesNotExist:
            return JsonResponse({"code": 400, "msg": "用户不存在!"})
        new_password = request.POST.get("new_password", '')
        check_password = request.POST.get("check_password", '')
        old_password = request.POST.get("old_password", '')
        if all([new_password, check_password, old_password]):
            if new_password != check_password:
                return JsonResponse({"code": 500, "msg": "两次密码不一致，请核对后输入！！！"})
            user.password = new_password
            user.save()
            comment = "{}用户重置{}用户密码成功".format(request.user, user.username)
            query_dict = {"user": user.username, "new_password": new_password, "check_password": check_password,
                          "old_password": old_password}
            recording_log(request, query_dict, comment)
            return JsonResponse({"code": 200, "msg": "重置密码成功！！！"})
        else:
            return JsonResponse({"code": 500, "msg": "参数有误，请重新输入！！！"})
