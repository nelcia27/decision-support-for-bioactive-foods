import re
from django.contrib.auth.models import User


def password_check(password,password2):

    # calculating the length
    length_error = len(password) < 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

    # overall result
    password_ok = ( length_error or digit_error or uppercase_error or lowercase_error or symbol_error )

    if password!=password2:
        password_msg = 'password1 != password2'
    else:
        password_msg = 'password too weak'

    return password_ok,password_msg


def clean_username(username):
    if len(User.objects.filter(username=username))>0:
        return 1
    else:
        return 0