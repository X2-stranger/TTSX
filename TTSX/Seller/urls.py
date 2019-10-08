from django.urls import path, re_path
from Seller.views import *

urlpatterns = [
    path('index/', index),
    path('login/', login),
    path('slc/', send_login_code),
    path('register/', cache_page(60 * 15)(register)),
    path('logout/', logout),
    path('personal_info',personal_info),
]
