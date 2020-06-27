from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class MyAuthenticationMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.path != '/users/login/' and not request.user.is_authenticated:
            return redirect('users:login')
