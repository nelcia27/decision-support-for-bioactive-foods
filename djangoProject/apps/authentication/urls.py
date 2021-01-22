from django.urls import path, include
from django.contrib import admin
from django.urls import path
from .views import *
from rest_framework import routers


urlpatterns = [
    path("authentication/register/", register, name="register"),
    path("authentication/get_users/", get_users, name="get_users"),
    path("authentication/delete_user/", delete_user, name="delete_user"),
    path("authentication/change_email/", change_email, name="change_email"),
    path("authentication/change_password/", change_password, name="change_password")# <-- added
]