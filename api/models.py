from django.db import models
from pathlib import Path
import os

# Create your models here.

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_PATH = os.path.join(BASE_DIR, 'mediafiles')

class Recorrencia(models.Model):
    cliente_CPF_CNPJ = models.BigIntegerField() # titular do pedido
    data = models.DateField() # data em que o pedido foi feito/entregue
    n_pedido = models.CharField(max_length=32, unique=True) # numero/id do pedido
    nome_razao_social = models.CharField(max_length=128) # nome do titular
    pedido_valor = models.FloatField() # valor do pedido


class ExcelFile(models.Model): 
    file = models.FileField()
    title = models.CharField(max_length=80)
    upload_date = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False, blank=True)



