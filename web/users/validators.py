from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import models


def validate_pwd(pwd, pwd2):
    if not pwd or not pwd2:
        raise ValidationError('Password is required')

    if len(pwd) < 6:
        raise ValidationError('Password should be at least 6 characters')

    if not set('[~!@#$%^&*()_-+={}":;\',.<>\|/?]+$').intersection(pwd):
        raise ValidationError('Password should contain at least 1 special character')

    if pwd != pwd2:
        raise ValidationError('Passwords don\'t match')


def validate_email(email):
    if not email:
        raise ValidationError('Email is required')

    try:
        validator = EmailValidator()
        validator.__call__(email)
    except ValidationError:
        raise ValidationError('Invalid email format')


def validate_image(field_file_obj):
    file_size = field_file_obj.file.size
    megabyte_limit = settings.MAX_BUSINESS_IMAGE_SIZE
    if file_size > megabyte_limit:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


def validate_name(name, pk):
    if get_user_model().objects.filter(name=name).exclude(models.Q(pk=pk) | models.Q(name='')):
        raise ValidationError({'name': 'There is already an account associated with that user name'})
    return name
