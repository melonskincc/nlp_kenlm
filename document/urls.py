from django.urls import path
from document.views import *

app_name = 'document'

urlpatterns = [
    path('index/', index, name='index'),
    path('upload_correction/', upload_correction, name='upload_correction'),
    path('download/', download, name='download')
]
