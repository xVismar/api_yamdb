import re
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework import status

# def user_validate(attrs):
#     """Check username for pattern compliance."""

#     username = attrs.get('username')
#     matching_chars = re.findall(r'[^\w.@+-]+', username)
#     if username == 'me' and matching_chars:
#         raise ValidationError(
#         f'Invalid characters in the username field: {matching_chars} '
#         f'or "me" used as the username.'
#     )
#     return attrs

def user_validate(attrs):
    username = attrs.get('username')
    if not isinstance(username, str):
        raise ValidationError("Username must be a string.")
    if not re.findall(r'^[\w.@+-]+\Z', username):
        raise ValidationError("Invalid username format.")