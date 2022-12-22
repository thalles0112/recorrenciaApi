from api import views
from rest_framework import routers
from django.urls import re_path
from django.conf.urls import include
from .views import  PedidosClientes, NaoRecorrente

router = routers.DefaultRouter()



urlpatterns = [
    re_path('nao-recorrente', NaoRecorrente.as_view()),
    re_path('recorrente', PedidosClientes.as_view()),
    
    
 
]