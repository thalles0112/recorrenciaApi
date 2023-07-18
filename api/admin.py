from django.contrib import admin
from .models import *
from django.contrib.admin import ModelAdmin

# Register your models here.
@admin.register(Recorrencia)
class RecorrenciaAdmin(ModelAdmin):
    
    fields = ('cliente_CPF_CNPJ',
              'data',
              'n_pedido',
              'nome_razao_social',
              'pedido_valor',
              'produtos',
              )
    list_display = ['id',]

@admin.register(ExcelFile)
class FileAdmin(ModelAdmin):
    fields = ('file',)
    list_display = ['file', 'id']

