from django.db import models
from pathlib import Path
import os

# Create your models here.

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_PATH = os.path.join(BASE_DIR, 'mediafiles')

class Produto(models.Model):
    sku_nome = models.CharField(max_length=128)
    sku_ref = models.CharField(max_length=16, unique=True)
    sku_url = models.CharField(max_length=255)

    def data(self):
        return({'sku_nome':self.sku_nome, 'sku_ref':self.sku_ref, 'sku_url':self.sku_url})
    


class Recorrencia(models.Model):
    cliente_CPF_CNPJ = models.BigIntegerField() # titular do pedido
    data = models.DateField() # data em que o pedido foi feito/entregue
    n_pedido = models.CharField(max_length=32, unique=True) # numero/id do pedido
    nome_razao_social = models.CharField(max_length=128) # nome do titular
    pedido_valor = models.FloatField() # valor do pedido
    produtos = models.ManyToManyField(Produto, blank=True, default='')


class ExcelFile(models.Model): 
    file = models.FileField()
    title = models.CharField(max_length=80)
    upload_date = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=16, default='cadastro')
    processed = models.BooleanField(default=False, blank=True)



