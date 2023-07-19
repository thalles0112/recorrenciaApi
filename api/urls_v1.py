from api import views
from rest_framework import routers
from django.urls import re_path
from django.conf.urls import include
from .views import  *



urlpatterns = [
    re_path('file-upload', FileUploadViewSet.as_view()),
    re_path('process-file', ProcessSheet.as_view()),
    re_path('add-product', AddProdutosToPedidos.as_view()),
    re_path('auth', CustomObtainAuthToken.as_view())
]



