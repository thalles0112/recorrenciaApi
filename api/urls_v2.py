from api import views
from rest_framework import routers
from django.urls import re_path
from django.conf.urls import include

from .views2 import BuscaIntervalo, Intervalos3, TodosPedidos, BuscaPedidos  
from .views import CorrigirPedidos
router = routers.DefaultRouter()


urlpatterns = [
    re_path('intervalos-v2', Intervalos3.as_view()),
    re_path('pedidos', TodosPedidos.as_view()),
    re_path('filtro-intervalo', BuscaIntervalo.as_view()),
    re_path('caralho', BuscaPedidos.as_view()),
    re_path('corrigir', CorrigirPedidos.as_view())

]



