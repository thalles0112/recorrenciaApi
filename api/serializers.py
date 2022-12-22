from rest_framework.serializers import ModelSerializer
from .models import Recorrencia


class RecorrenciaSerializer(ModelSerializer):
    
    class Meta:
        model = Recorrencia
        fields = [
        #'id',
        'cliente_CPF_CNPJ',
        'data',
        #'n_pedido',
        #'nome_razao_social',
        #'pedido_pgmto',
        'pedido_valor'
        ]