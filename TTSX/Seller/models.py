from django.db import models


class LoginUser(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=32)
    username = models.CharField(max_length=32, null=True, blank=True)
    phone_number = models.CharField(max_length=11, null=True, blank=True)
    photo = models.ImageField(upload_to="images", default="images/default_photo.jpg")
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=32, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    user_type = models.IntegerField(default=0)  # 买家0  卖家1  管理员2


class Valid_Code(models.Model):
    code_content = models.CharField(max_length=32)
    code_user = models.EmailField()
    code_time = models.DateTimeField(auto_now=True)
    code_state = models.IntegerField(default=0)
