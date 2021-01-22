from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import json
# views.py
from django.shortcuts import render, redirect
from .forms import RegisterForm
import re
from .functions import *


@csrf_exempt
def register(response):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    response_data = {}

    if response.method == "POST":
        body_unicode = response.body.decode('utf-8')
        body = json.loads(body_unicode)
        name = body['username']
        email = body['email']
        password1 = body['password1']
        password2 = body['password2']
        response_data['result'] = 'error'
        psw, password_msg = password_check(password1, password2)
        if len(name) < 8:
            response_data['message'] = 'username len <8'
            response = HttpResponse(json.dumps(response_data))
            response.status_code = 400
            return (response)
        elif clean_username(name):
            response_data['message'] = 'username exist'
            response = HttpResponse(json.dumps(response_data))
            response.status_code = 400
            return (response)
        elif not re.search(regex, email):
            response_data['message'] = 'invalid email'
            response = HttpResponse(json.dumps(response_data))
            response.status_code = 400
            return (response)
        elif psw:
            response_data['message'] = password_msg
            response = HttpResponse(json.dumps(response_data))
            response.status_code = 400
            return (response)

        try:
            user = User.objects.create_user(username=name,
                                            email=email,
                                            password=password2)
        except:
            response_data['message'] = 'database error'
            response = HttpResponse(json.dumps(response_data))
            response.status_code = 500
            return (response)
        response_data['result'] = 'correct'
        response_data['message'] = 'user created'
        response = HttpResponse(json.dumps(response_data))
        response.status_code = 200
        return (response)
    response_data['message'] = 'not POST'
    response = HttpResponse(json.dumps(response_data))
    response.status_code = 400
    return (response)


@csrf_exempt
def get_users(response):
    response_data = {}
    if response.method == "GET":
        user = get_user_model()
        user_list = list(user.objects.values('username','email','is_superuser'))
        not_superuser = []
        for i in range(len(user_list)):
            if user_list[i]['is_superuser'] == False:
                not_superuser.append(user_list[i])
        response = HttpResponse(json.dumps(not_superuser))
        response.status_code = 200
        return (response)
    response_data['message'] = 'not GET'
    response = HttpResponse(json.dumps(response_data))
    response.status_code = 400
    return(response)

@csrf_exempt
def change_email(response):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    response_data = {}
    body_unicode = response.body.decode('utf-8')
    body = json.loads(body_unicode)
    name = body['username']
    email = body['email']
    if response.method == "POST":
        user = get_user_model()
        try:
            user_tmp = User.objects.get(username=name)
        except:
            response_data['message'] = 'uzytkownik nie istnieje'
            response = HttpResponse(json.dumps(response_data))
            response.status_code = 400
            return (response)
        if not re.search(regex, email):
            response_data['message'] = 'invalid email'
            response = HttpResponse(json.dumps(response_data))
            response.status_code = 400
            return (response)
        else:
            user_tmp.email = email
        user_tmp.save()
        response_data['message'] = 'mail zostal zmieniony'
        response = HttpResponse(json.dumps(response_data))
        response.status_code = 200
        return (response)
    response_data['message'] = 'not POST'
    response = HttpResponse(json.dumps(response_data))
    response.status_code = 400
    return(response)

@csrf_exempt
def change_password(response):
    response_data = {}
    body_unicode = response.body.decode('utf-8')
    body = json.loads(body_unicode)
    name = body['username']
    password = body['password']
    if response.method == "POST":
        user = get_user_model()
        try:
            user_tmp = User.objects.get(username=name)
        except:
            response_data['message'] = 'uzytkownik nie istnieje'
            response = HttpResponse(json.dumps(response_data))
            response.status_code = 400
            return (response)
        user_tmp.set_password(password)
        user_tmp.save()
        response_data['message'] = 'haslo zmienione'
        response = HttpResponse(json.dumps(response_data))
        response.status_code = 200
        return (response)
    response_data['message'] = 'not POST'
    response = HttpResponse(json.dumps(response_data))
    response.status_code = 400
    return(response)

@csrf_exempt
def delete_user(response):
    response_data = {}
    body_unicode = response.body.decode('utf-8')
    body = json.loads(body_unicode)
    name = body['username']
    if response.method == "POST":
        user = get_user_model()
        try:
            user_tmp = User.objects.get(username=name)
            user_tmp.delete()
            response_data['message'] = 'urzytkownik usuniety'
            response = HttpResponse(json.dumps(response_data))
            response.status_code = 200
            return (response)
        except:
            response_data['message'] = 'uzytkownik nie istnieje'
            response = HttpResponse(json.dumps(response_data))
            response.status_code = 400
            return (response)
    response_data['message'] = 'not POST'
    response = HttpResponse(json.dumps(response_data))
    response.status_code = 400
    return(response)