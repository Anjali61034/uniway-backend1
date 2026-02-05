from django.shortcuts import redirect

from rest_framework.response import Response
from rest_framework import status
from .models import CustomToken

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group =  request.user.groups.all()[0].name
        if group == 'dept_head':
            return redirect('home')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def read_only_scope(view_func):
    def wrapper_func(self, *args, **kwargs):
        try:
            if self.request.auth and getattr(self.request.auth, 'key', None):
                token = CustomToken.objects.get(key=self.request.auth.key)
                if token.scope == CustomToken.READ_ONLY_SCOPE:
                    return view_func(self.request, *args, **kwargs)
                else:
                    return Response(
                        {"detail": "Insufficient scope for this resource."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            else:
                return Response(
                    {"detail": "Authentication information not present."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except CustomToken.DoesNotExist:
            return Response(
                {"detail": "Invalid or missing token."},
                status=status.HTTP_401_UNAUTHORIZED
            )
    return wrapper_func