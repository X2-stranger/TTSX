from django.urls import path, re_path
from Seller.views import *

urlpatterns = [
    path('index/', index),
    path('login/', login),
    path('slc/', send_login_code),
    path('register/', cache_page(60 * 15)(register)),
    path('logout/', logout),
    path('personal_info', personal_info),
    path('goods_list/', goods_list),
    re_path('goods_list/(?P<page>\d+)/(?P<status>[01])/', goods_list),
    re_path('goods_status/(?P<state>\w+)/(?P<id>\d+)/', goods_status),
    path('goods_add/', goods_add),
    path('ad/', add_goods),
]
