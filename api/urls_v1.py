from api import views
from rest_framework import routers
from django.urls import re_path
from django.conf.urls import include
from .views import  *
router = routers.DefaultRouter()




urlpatterns = [
    re_path(r'^', include(router.urls)),
    re_path('nao-recorrente', NaoRecorrente.as_view()),
    re_path('recorrente', PedidosClientes.as_view()),
    re_path('busca-cpf', BuscaCpf.as_view()),
    re_path('intervalos', Intervalos.as_view()),
    re_path('filtro-intervalo', BuscaIntervalo.as_view()),
    re_path('file-upload', FileUploadViewSet.as_view()),
    re_path('process-file', ProcessSheet.as_view()),
    re_path('add-product', AddProdutosToPedidos.as_view()),
    re_path('auth', CustomObtainAuthToken.as_view())

]



