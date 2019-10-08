import time, datetime, hashlib
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from Seller.models import *
from django.views.decorators.csrf import csrf_exempt  # 免除csrf保护
from django.http import JsonResponse


# 登录验证
def loginValid(fun):
    def inner(request, *args, **kwargs):
        cookie_username = request.COOKIES.get("username")
        session_username = request.session.get("username")
        if cookie_username and session_username and cookie_username == session_username:
            return fun(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/Seller/login/")

    return inner


# 加密
def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result


# 验证码
import requests
import json
import random
from TTSX.settings import DING_URL


def random_code(len=4):
    """
         生成6位验证码
    """
    string = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    valid_code = "".join([random.choice(string) for i in range(len)])
    return valid_code


def sendDing(content, to=None):
    headers = {
        "Content-Type": "application/json",
        "Charset": "utf-8"
    }
    requests_data = {
        "msgtype": "text",
        "text": {
            "content": content
        },
        "at": {
            "atMobiles": [

            ],
            "isAtAll": True
        }
    }
    if to:
        requests_data["at"]["atMobiles"].append(to)
        requests_data["at"]["isAtAll"] = False
    else:
        requests_data["at"]["atMobiles"].clear()
        requests_data["at"]["isAtAll"] = True
    sendData = json.dumps(requests_data)
    response = requests.post(url=DING_URL, headers=headers, data=sendData)
    content = response.json()
    return content


@csrf_exempt
def send_login_code(request):
    result = {
        "code": 200,
        "data": ""
    }
    if request.method == "POST":
        email = request.POST.get("email")
        code = random_code()
        c = Valid_Code()
        c.code_user = email
        c.code_content = code
        c.save()
        send_data = "%s的验证码是%s,测试测试" % (email, code)
        sendDing(send_data)
        result["data"] = "发送成功"
    else:
        result["code"] = 400
        result["data"] = "请求错误"
    return JsonResponse(result)


# 首页
@loginValid
def index(request):
    return render(request, "seller/index.html", locals())


# 注册
def register(request):
    error_message = ""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        if email:
            # 首先检测email有没有
            user = LoginUser.objects.filter(email=email).first()
            if not user:
                new_user = LoginUser()
                new_user.email = email
                new_user.username = email
                new_user.password = setPassword(password)
                new_user.save()
            else:
                error_message = "邮箱已经被注册，请登录"
        else:
            error_message = "邮箱不可以为空"
    return render(request, "seller/register.html", locals())


from django.views.decorators.cache import cache_page


# 登录
@cache_page(60 * 15)  # 使用缓存，缓存寿命15分钟
def login(request):
    error_message = ""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        code = request.POST.get("valid_code")
        if email:
            # 首先检测email有没有
            user = LoginUser.objects.filter(email=email).first()
            if user:
                db_password = user.password
                password = setPassword(password)
                if db_password == password:
                    # 获取验证码
                    codes = Valid_Code.objects.filter(code_user=email).order_by("-code_time").first()
                    # 检验验证码是否存在，是否过期，是否被使用
                    now = time.mktime(datetime.datetime.now().timetuple())
                    db_time = time.mktime(codes.code_time.timetuple())
                    t = (now - db_time) / 60
                    if codes and codes.code_state == 0 and t <= 5 and codes.code_content.upper() == code.upper():
                        response = HttpResponseRedirect("/Seller/index/")
                        response.set_cookie("username", user.username)
                        response.set_cookie("user_id", user.id)
                        request.session["username"] = user.username

                        return response
                    else:
                        error_message = "验证码错误"
                else:
                    error_message = "密码错误"
            else:
                error_message = "用户名不存在"
        else:
            error_message = "邮箱不可以空"
    return render(request, "seller/login.html", locals())


# 登出/注销
def logout(request):
    response = HttpResponseRedirect("/login/")
    keys = request.COOKIES.keys()
    for key in keys:
        response.delete_cookie(key)
    del request.session["username"]
    return response
