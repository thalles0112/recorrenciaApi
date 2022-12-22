from django.db import models

# Create your models here.
class Recorrencia(models.Model):
    cliente_CPF_CNPJ = models.BigIntegerField() # titular do pedido
    data = models.DateField() # data em que o pedido foi feito/entregue
    n_pedido = models.CharField(max_length=32) # numero/id do pedido
    nome_razao_social = models.CharField(max_length=128) # nome do titular
    pedido_pgmto = models.CharField(max_length=64) # forma de pagamento usada no pedido
    pedido_valor = models.FloatField() # valor do pedido
