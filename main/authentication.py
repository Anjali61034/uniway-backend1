from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from .models import CustomToken
from rest_framework.exceptions import AuthenticationFailed

class UserLessTokenAuthentication(TokenAuthentication):
    model = CustomToken

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.get(key=key)
            if token.scope != CustomToken.READ_ONLY_SCOPE:
                raise AuthenticationFailed('Invalid scope for this resource')
            return None, token
        except model.DoesNotExist:
            raise AuthenticationFailed('Invalid token')