from django.urls import path
from users.views import *

app_name = 'users'

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('verify_code/', verify_code, name='verify_code')
]
