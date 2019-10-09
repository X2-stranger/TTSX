from Buyer.views import *
from django.urls import path, re_path

urlpatterns = [
    path('login/', login),
    path('register/', register),
    path('index/', index),
    path('logout/', logout),
]
