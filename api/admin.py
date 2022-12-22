from django.contrib import admin
from .models import Recorrencia
from django.contrib.admin import ModelAdmin

# Register your models here.
@admin.register(Recorrencia)
class RecorrenciaAdmin(ModelAdmin):
    
    fields = ('id',)
    list_display = ['id',]