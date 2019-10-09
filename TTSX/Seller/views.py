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


# 个人主页
@loginValid
def personal_info(request):
    user_id = request.COOKIES.get("user_id")
    user = LoginUser.objects.get(id=int(user_id))
    if request.method == "POST":
        user.username = request.POST.get("username")
        user.gender = request.POST.get("gender")
        user.age = request.POST.get("age")
        user.phone_number = request.POST.get("phone_number")
        user.address = request.POST.get("address")
        user.photo = request.FILES.get("photo")
        user.save()
    return render(request, "seller/personal_info.html", locals())


# 商品列表
from django.core.paginator import Paginator


@loginValid
def goods_list(request, status, page=1):
    user_id = request.COOKIES.get("user_id")
    user = LoginUser.objects.get(id=int(user_id))
    page = int(page)
    if status == "1":
        goodses = Goods.objects.filter(goods_store=user, goods_status=1)
    elif status == "0":
        goodses = Goods.objects.filter(goods_store=user, goods_status=0)
    else:
        goodses = Goods.objects.all()
    all_goods = Paginator(goodses, 10)
    goods_list = all_goods.page(page)
    return render(request, "seller/goods_list.html", locals())


# 上架/下架
@loginValid
def goods_status(request, state, id):
    id = int(id)
    goods = Goods.objects.get(id=id)
    if state == "up":
        goods.goods_status = 1
    elif state == "down":
        goods.goods_status = 0
    goods.save()
    url = request.META.get("HTTP_REFERER", "/goods_list/1/1")
    return HttpResponseRedirect(url)


# 商品添加
@loginValid
def goods_add(request):
    goods_type_list = GoodsType.objects.all()
    if request.method == "POST":
        data = request.POST
        files = request.FILES

        goods = Goods()
        # 常规保存
        goods.goods_number = data.get("goods_number")
        goods.goods_name = data.get("goods_name")
        goods.goods_price = data.get("goods_price")
        goods.goods_count = data.get("goods_count")
        goods.goods_location = data.get("goods_location")
        goods.goods_safe_date = data.get("goods_safe_date")
        goods.goods_pro_time = data.get("goods_pro_time")  # 出厂日期格式必须是yyyy-mm-dd格式
        goods.goods_status = 1

        # 保存外键类型
        goods_type_id = int(data.get("goods_type"))
        goods.goods_type = GoodsType.objects.get(id=goods_type_id)
        # 保存图片
        picture = files.get("picture")
        goods.picture = picture
        # 保存对应的卖家
        user_id = request.COOKIES.get("user_id")
        goods.goods_store = LoginUser.objects.get(id=int(user_id))

        goods.save()

    return render(request, "seller/goods_add.html", locals())


import random


def add_goods(request):
    goods_name = "大葱、小葱、蒜、洋葱、生姜、洋姜、莲菜、莴笋、山药、茭白、马铃薯、红薯、卜留克、芦笋、甘蓝、百合、莲藕、大白菜、小白菜、抱子甘蓝、羽衣甘蓝、紫甘蓝、结球甘蓝、生菜、菠菜、韭菜、芹菜、苦苣、油麦菜、黄秋葵、空心菜、茼蒿、苋菜、香椿、娃娃菜、芥兰、荠菜、香菜、茴香、马齿苋、木耳叶、芥菜、芜荽（大叶香菜、小叶香菜）、雪里蕻、油菜、紫苏、黑芝麻、香椿芽、萝卜芽、荞麦芽、花生芽、姜芽、黄豆芽、绿豆芽、香菇、木耳、草菇、平菇、秀珍菇、金针菇、杏鲍菇、茶树菇、银耳、猴头菇、南瓜、金丝南瓜、黑皮冬瓜、苦瓜、黄瓜、丝瓜、菜瓜、瓠瓜、胡瓜、佛手瓜、西葫芦、番茄、茄子、芸豆、豇豆、豌豆、架豆、刀豆、扁豆、菜豆、毛豆、蛇豆、甜玉米".replace(
        " ", "、")
    goods_name = goods_name.split("、")
    goods_address = "河北，山西，辽宁，吉林，黑龙江，江苏，浙江，安徽，福建，江西，山东，河南，湖北，湖南，广东，海南，四川，贵州，云南，陕西，甘肃，青海，台湾".split("，")
    for j, i in enumerate(range(100), 1):
        goods = Goods()
        goods.goods_number = str(j).zfill(5)
        goods.goods_name = random.choice(goods_address) + random.choice(goods_name)
        goods.goods_price = random.random() * 100
        goods.goods_count = random.randint(30, 100)
        goods.goods_location = random.choice(goods_address)
        goods.goods_safe_date = random.randint(1, 36)
        goods.goods_status = 1
        goods.goods_store.id = 6
        goods.save()
    return HttpResponse("hello world")