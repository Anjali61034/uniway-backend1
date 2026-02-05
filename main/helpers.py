from rest_framework.authtoken.models import Token
from .models import CustomToken

def create_read_only_token():
    token, _ = CustomToken.objects.get_or_create()
    token.scope = CustomToken.READ_ONLY_SCOPE
    token.save()
    return token

def convert_to_dept_name(username):
    result = username[0]  
    for char in username[1:]:
        if char.isupper():
            result += ' ' + char  # Insert a space before each capital letter
        else:
            result += char
    return result