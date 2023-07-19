from django.shortcuts import render
from numpy import delete
from rest_framework.viewsets import ModelViewSet
from .serializers import  RecorrenciaSerializer
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import filters, status
import json
import datetime
from django.core.files.storage import FileSystemStorage
from .readExcel import excel2peewee_data_formatter
import pandas as pd
from pathlib import Path
import os
from threading import Thread, Lock
from typing import List
from .serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

# Create your models here.


BASE_DIR = Path(__file__).parent.parent
lock = Lock()


def chunk(lst: List, num_parts: int) -> List[List]:
    size = len(lst) // num_parts  # tamanho de cada sub-lista
    remainder = len(lst) % num_parts  # elementos restantes

    result = []
    start = 0

    for i in range(num_parts):
        if i < remainder:
            end = start + size + 1
        else:
            end = start + size

        result.append(lst[start:end])
        start = end

    return result

def ProcessMany(excel_data):
    for data in excel_data:
        lock.acquire()
      
        date_object = datetime.datetime.fromisoformat(data['data'].split(' ')[0])
        data['data'] = f'{date_object.year}-{date_object.month}-{date_object.day}'
        
        serializer = RecorrenciaSerializer(data=data)
        if serializer.is_valid():
            try:
                serializer.save()
            except Exception as e:
                print(e)


    
        lock.release()

class ProcessSheet(APIView):
    authentication_classes = [TokenAuthentication,]
    def post(self, request, *args, **kwargs):
        sheet_id = self.request.data['id']
        
        porra = str(BASE_DIR)

        excel_obj = ExcelFile.objects.get(id=sheet_id)

        filename = str(excel_obj.file).split('/')[2]
        full_path = os.path.join(porra, f'mediafiles/{filename}')

        excel_data = excel2peewee_data_formatter(full_path, 'Plan1')
       
        
        new_excel_data = chunk(excel_data, 4)
        tarefas = []

 
        
        
        for data in new_excel_data:
            tarefa = Thread(target=ProcessMany, args=([data]))
            tarefas.append(tarefa)
            tarefa.start()

        

        for tarefa in tarefas:
            tarefa.join()
    
        return Response({'status':'processado' })

class CorrigirPedidos(APIView):
    authentication_classes = [TokenAuthentication,]
    def post(self, request, *args, **kwargs):
        sheet_id = self.request.data['id']
        
        porra = str(BASE_DIR)
        
        excel_obj = ExcelFile.objects.get(id=sheet_id)

        filename = str(excel_obj.file).split('/')[2]
        full_path = os.path.join(porra, f'mediafiles/{filename}')

        excel_data = excel2peewee_data_formatter(full_path, 'Plan1')
       
        
        for data in excel_data:
            try:
                pedido = Recorrencia.objects.get(n_pedido=data['n_pedido'])
                pedido.pedido_valor = data['pedido_valor']
                pedido.save()
            except:
                pass
    
        return Response({'status':'processado' })


class AddProdutosToPedidos(APIView):
    def post(self, request, *args, **kwargs):
        sheet_id = self.request.data['id']
        
        porra = str(BASE_DIR)
        
        excel_obj = ExcelFile.objects.get(id=sheet_id)

        filename = str(excel_obj.file).split('/')[2]
        full_path = os.path.join(porra, f'mediafiles/{filename}')
        excel_data = excel2peewee_data_formatter(full_path, 'Plan1')
        errors = []
        line = 1
        for data in excel_data:
            try:
                pedido = Recorrencia.objects.get(n_pedido=data['n_pedido'])
                produto = Produto.objects.get_or_create(sku_ref=data['sku_ref'], sku_nome=data['sku_nome'], sku_url=data['sku_url'])
              
                
                if type(produto) == tuple:
                    pedido.produtos.add(produto[0])
                else:
                    pedido.produtos.add(produto)
                

            except Exception as e:
                
                errors.append(f'linha {line}: {e}')
                print(f'linha {line}: {e}')
            line += 1
        
        excel_obj.processed = True
        excel_obj.save()
        
        return Response({'status':'processado', 'errors':errors})


class FileUploadViewSet(APIView):
    authentication_classes = [TokenAuthentication,]
    def post(self,request):
        file = request.FILES.get('file')
       
       
        if not file:
            return Response({'error': 'No file was uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_url = fs.url(filename)

        newFile = ExcelFile(title=filename, file=file_url, file_type=self.request.data['file_type'])
        newFile.save()



        return Response({'id': newFile.id, 'title': filename, 'file':file_url, 'upload_date': newFile.upload_date, 'file_type':newFile.file_type}, status=status.HTTP_201_CREATED)

    def get(self, request):
        queryset = ExcelFile.objects.all().order_by('-id')
        res = []
        for obj in queryset:
            res.append({'id':obj.id,'title': obj.title, 'file':f'http://10.0.0.160:8000/{BASE_DIR}/{obj.file}', 'upload_date':obj.upload_date, 'processed': obj.processed, 'file_type':obj.file_type})


 
        return Response(res)


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = User.objects.get(id=token.user_id)
        userSerializer = UserSerializer(user, many=False)

        return Response({'token': token.key, 'user': userSerializer.data})