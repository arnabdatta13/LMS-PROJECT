from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.http.request import HttpRequest

class EmailBackEnd(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)  # login by email
        except UserModel.DoesNotExist:  # Correct the attribute name here
            return None
        else:
            if user.check_password(password):
                return user
        return None
