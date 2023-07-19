from api import views
from rest_framework import routers
from django.urls import re_path
from django.conf.urls import include

from .views2 import * 
from .views import CorrigirPedidos
router = routers.DefaultRouter()


urlpatterns = [
    re_path('caralho', BuscaPedidos.as_view()),
    re_path('corrigir', CorrigirPedidos.as_view()),
    re_path('filtrar-recorrentes-por-periodo', TodosPedidosRecorrentes.as_view()),
    re_path('filtrar-novos-por-periodo', TodosPedidosNovos.as_view()),
    re_path('produtos-recorrentes', ProdutoDePedidos.as_view()),
    re_path('produtos-novos', ProdutoDePedidosNovos.as_view()),
    re_path('clientes', ClientesView.as_view()),
]



