from django.shortcuts import render
from django.http import HttpResponseRedirect
from Seller.models import *
from Seller.views import setPassword


def loginValid(fun):
    def inner(request, *args, **kwargs):
        cookie_user = request.COOKIES.get("username")
        session_user = request.session.get("username")
        if cookie_user and session_user and cookie_user == session_user:
            return fun(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/Buyer/login/")

    return inner


import logging

collect = logging.getLogger("django")


# 登录
def login(request):
    if request.method == "POST":
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        user = LoginUser.objects.filter(email=email).first()
        if user:
            db_password = user.password
            password = setPassword(password)
            if db_password == password:
                response = HttpResponseRedirect("/Buyer/index/")
                response.set_cookie("username", user.username)
                response.set_cookie("user_id", user.id)
                request.session["username"] = user.username

                collect.debug("%s is login" % user.username)

                return response
    return render(request, "buyer/login.html")


# 注册
def register(request):
    if request.method == "POST":
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")

        user = LoginUser()
        user.username = username
        user.password = setPassword(password)
        user.email = email
        user.save()
        return HttpResponseRedirect("/Buyer/login/")
    return render(request, "buyer/register.html")


# 登出
def logout(request):
    url = request.META.get("HTTP_REFERER", "/Buyer/index/")
    response = HttpResponseRedirect(url)
    for k in request.COOKIES:
        response.delete_cookie(k)
    del request.session["username"]
    return response


def index(request):
    goods_type = GoodsType.objects.all()  # 获取所有类型
    result = []
    for ty in goods_type:
        # 按照生产日期对对应类型的商品进行排序
        goods = ty.goods_set.order_by("-goods_pro_time")
        if len(goods) >= 4:  # 进行条件判断
            goods = goods[:4]
            result.append({"type": ty, "goods_list": goods})
    return render(request, "buyer/index.html", locals())
