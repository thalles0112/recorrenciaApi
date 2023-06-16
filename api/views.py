from django.shortcuts import render
from numpy import delete
from rest_framework.viewsets import ModelViewSet
from .serializers import  RecorrenciaSerializer
from .models import Recorrencia, ExcelFile
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


class BaseRecorrenciaViewset(ModelViewSet):
    authentication_classes = [TokenAuthentication,]
    serializer_class = RecorrenciaSerializer
    queryset = Recorrencia.objects.all() 

class FileUploadViewSet(APIView):
    authentication_classes = [TokenAuthentication,]
    def post(self,request):
        file = request.FILES.get('file')
        print(file)
        if not file:
            return Response({'error': 'No file was uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_url = fs.url(filename)

        newFile = ExcelFile(title=filename, file=file_url)
        newFile.save()



        return Response({'id': newFile.id, 'title': filename, 'file':file_url, 'upload_date': newFile.upload_date}, status=status.HTTP_201_CREATED)

    def get(self, request):
        queryset = ExcelFile.objects.all().order_by('-id')
        res = []
        for obj in queryset:
            res.append({'id':obj.id,'title': obj.title, 'file':f'http://10.0.0.160:8000/{BASE_DIR}/{obj.file}', 'upload_date':obj.upload_date, 'processed': obj.processed})



        return Response(res)


    

      
class PedidosClientes(APIView):
    authentication_classes = [TokenAuthentication,]
    print()
    serializer_class = RecorrenciaSerializer
    
    filter_backends = [filters.OrderingFilter]
    ordering = ['cliente_CPF_CNPJ', 'data']

    def get(self, request, format=None):
 
        objects = Recorrencia.objects.all()

        cpfs = []
        counter = {}
        recorrent_clients = []
        for object in objects:
           
                
            if object.cliente_CPF_CNPJ not in counter:
                counter[object.cliente_CPF_CNPJ] = 0
            counter[object.cliente_CPF_CNPJ] +=1 

        page_arg = self.request.query_params.get('page', None)
        max_interval_arg = self.request.query_params.get('max-interval', None)
        min_interval_arg = self.request.query_params.get('min-interval', None)
        
        for client in counter.items():
            if int(client[1]) > 1:
                recorrent_clients.append(client[0])
            
        queryset = Recorrencia.objects.filter(cliente_CPF_CNPJ__in=recorrent_clients).order_by('cliente_CPF_CNPJ', '-data')
        

###########################################################
        new_res = []
        new_cli = {}

        

        for p in queryset:
            if f"<{p.cliente_CPF_CNPJ}/>" not in new_cli:
                new_cli[f"<{p.cliente_CPF_CNPJ}/>"] = []
            try:

                new_cli[f"<{p.cliente_CPF_CNPJ}/>"].append({"data":p.data.isoformat(),"valor":p.pedido_valor, "n_pedido":p.n_pedido})    
            except:
                pass
            

        new_cli = str(new_cli)[1:-2].replace("'", '"')
        new_cli = str(new_cli).split('],')



        for n in new_cli:
            try:
                formated_string = '{'+'"cliente"'+':'+n[n.index('<')+1:n.index('/>')]+','+n+']'+'}'.replace(' ', '')
                
                formated_string = formated_string.replace(formated_string[formated_string.index('<'):formated_string.index('/>')+2], 'pedidos')
                
                new_res.append(json.loads(formated_string))
            except Exception as e:
                print(e)
                break

        client_num = 0
        format = '%Y/%m/%d'
        prevdata=datetime.datetime
        iter_count = 0
        delta = datetime.timedelta()
        deltas = []
        valores = []

        main_valores = []
        main_delta = []
    
        def average(days):
            soma = 0
            try:
                soma = sum(days)/len(days)    
            except:
                pass
            return soma

        for res in new_res:
           
            iter_count = 0   
            for data in res['pedidos']:
                dataobj = datetime.datetime.strptime(data['data'].replace('-', '/'), format)
                valor = data['valor']
                valores.append(valor)
                if iter_count == 0:
                    prevdata = dataobj
                    iter_count += 1
                    continue
                else:
                    try:
                        delta = prevdata - dataobj
                                
                    except:
                        pass
                
                    deltas.append(delta.days)
                prevdata=dataobj
                
            try:
                main_delta.append(average(deltas)) # adicionando os intervalos de um 
                main_valores.append(average(valores)) # cliente a lista de intervalos gerais
            except Exception as e:
                pass

            res['ticket_medio'] = average(valores)

            if len(deltas)>=2:
                res['intervalo'] = average(deltas)
            else:
                res['intervalo'] = delta.days
           
            
            
            deltas.clear()
            valores.clear()

        

        new_res.insert(0, {"resumo": {
                            "valor_menor":min(main_valores),
                            "valor_maior":max(main_valores) ,
                            "intervalo_maior": max(main_delta),
                            "intervalo_medio":average(main_delta),
                            "valor_medio":average(main_valores),
                            "intervalo_menor": min(main_delta),
                            "total_lenght": int(len(new_res)/100),
                            }
                            
                            })
        main_delta.remove(0)
        new_res[0]["resumo"]["intervalo_menor"] = min(main_delta)
        
        
        #calculando a media dos intervalos e inserindo na lista que
        # vai ser retornada à api
    
        if int(page_arg) == 0:
            return Response(new_res)         
            

        else:
            if int(page_arg)> 1:
                    formated_res = (new_res[(int(page_arg)*100)-99:(int(page_arg)*100)+1])
                    formated_res.insert(0, new_res[0])
                    return Response(formated_res)
            else:
                return Response(new_res[(int(page_arg)*100)-100:int(page_arg)*100])

    
             

class NaoRecorrente(APIView):
    authentication_classes = [TokenAuthentication,]
    serializer_class = RecorrenciaSerializer
    
    filter_backends = [filters.OrderingFilter]
    ordering = ['cliente_CPF_CNPJ', 'data']

    def get(self, request, format=None):
        
        objects = Recorrencia.objects.all()
        cpfs = []
        counter = {}
        recorrent_clients = []
        for object in objects:
            if object.cliente_CPF_CNPJ not in counter:
                counter[object.cliente_CPF_CNPJ] = 0
            counter[object.cliente_CPF_CNPJ] +=1 

        cpf_arg = self.request.query_params.get('cpf', None)
        page_arg = self.request.query_params.get('page', None)
        
        for client in counter.items():
            
            if int(client[1]) < 2:
                
                recorrent_clients.append(client[0])
            
        if cpf_arg is not None:
            queryset = Recorrencia.objects.filter(cliente_CPF_CNPJ=cpf_arg)
        else:
            recorrent_clients.append(cpf_arg)
            queryset = Recorrencia.objects.filter(cliente_CPF_CNPJ__in=recorrent_clients).order_by('cliente_CPF_CNPJ', '-data')
        

###########################################################
        new_res = []
        new_cli = {}

        

        for p in queryset:

            if f"<{p.cliente_CPF_CNPJ}/>" not in new_cli:
                new_cli[f"<{p.cliente_CPF_CNPJ}/>"] = []
            try:

                new_cli[f"<{p.cliente_CPF_CNPJ}/>"].append({"data":p.data.isoformat(),"valor":p.pedido_valor, "n_pedido":p.n_pedido})    
            except:
                pass
            

        new_cli = str(new_cli)[1:-2].replace("'", '"')
        new_cli = str(new_cli).split('],')



        for n in new_cli:
            try:                                        # essa parte aqui e para colocar o cpf em frente a chave "CLIENTE"
                formated_string = '{'+'"cliente"'+':'+n[n.index('<')+1:n.index('/>')]+','+n+']'+'}'.replace(' ', '')
                
                formated_string = formated_string.replace(formated_string[formated_string.index('<'):formated_string.index('/>')+2], 'pedidos')
                
                new_res.append(json.loads(formated_string))
            except Exception as e:
                print(e)
                break

        client_num = 0
        format = '%Y/%m/%d'
        prevdata=datetime.datetime
        iter_count = 0
        
        deltas = []
        valores = []

        main_valores = []
        main_delta = []
    
        def average(days):
            
            try:
                soma = sum(days)/len(days)    
            except:
                pass
            return soma

        for res in new_res:   
            for data in res['pedidos']:
                valor = data['valor']
                valores.append(valor)

            try:
                 # adicionando os intervalos de um 
                main_valores.append(average(valores))                                    # cliente a lista de intervalos gerais
            except Exception as e:
                pass
            
            iter_count += 1
            valores.clear()
        
        
        
        new_res.insert(0, {"resumo":{
            "valor_medio":average(main_valores),
            "valor_menor":min(main_valores),
            "valor_maior":max(main_valores),
            "total_lenght": int(len(new_res)/100)
                }
            
            })
        #calculando a media dos intervalos e inserindo na lista que
        # vai ser retornada à api

        if int(page_arg) == 0:
            return Response(new_res)         
            
        else:
            if int(page_arg)> 1:
                
                formated_res = (new_res[(int(page_arg)*100)-99:(int(page_arg)*100)+1])
                formated_res.insert(0, new_res[0])
                return Response(formated_res)
            else:
                return Response(new_res[(int(page_arg)*100)-100:int(page_arg)*100])

class BuscaCpf(APIView):
    authentication_classes = [TokenAuthentication,]
    serializer_class = RecorrenciaSerializer
    
    filter_backends = [filters.OrderingFilter]
    ordering = ['cliente_CPF_CNPJ', 'data']

    def get(self, request, format=None):
 
        objects = Recorrencia.objects.all()

        cpfs = []
        counter = {}
        recorrent_clients = []
        for object in objects:
            if object.cliente_CPF_CNPJ not in counter:
                counter[object.cliente_CPF_CNPJ] = 0
            counter[object.cliente_CPF_CNPJ] +=1 

        cpf_arg = self.request.query_params.get('cpf', None)
        
        
            
        
        queryset = Recorrencia.objects.filter(cliente_CPF_CNPJ=cpf_arg).order_by('-data')
        
        

###########################################################
        new_res = []
        new_cli = {}

        

        for p in queryset:
            if f"<{p.cliente_CPF_CNPJ}/>" not in new_cli:
                new_cli[f"<{p.cliente_CPF_CNPJ}/>"] = []
            try:

                new_cli[f"<{p.cliente_CPF_CNPJ}/>"].append({"data":p.data.isoformat(),"valor":p.pedido_valor, "n_pedido": p.n_pedido})    
            except:
                pass
            

        new_cli = str(new_cli)[1:-2].replace("'", '"')
        new_cli = str(new_cli).split('],')



        for n in new_cli:
            try:
                formated_string = '{'+'"cliente"'+':'+n[n.index('<')+1:n.index('/>')]+','+n+']'+'}'.replace(' ', '')
                
                formated_string = formated_string.replace(formated_string[formated_string.index('<'):formated_string.index('/>')+2], 'pedidos')
                
                new_res.append(json.loads(formated_string))
            except Exception as e:
                print(e)
                break

        client_num = 0
        format = '%Y/%m/%d'
        prevdata=datetime.datetime
        iter_count = 0
        delta = datetime.timedelta()
        deltas = []
        valores = []

        main_valores = []
        main_delta = []
    
        def average(days):
            soma = 0
            try:
                soma = sum(days)/len(days)    
            except:
                pass
            return soma

        for res in new_res:
            iter_count = 0   
            for data in res['pedidos']:
                dataobj = datetime.datetime.strptime(data['data'].replace('-', '/'), format)
                valor = data['valor']
                valores.append(valor)
                if iter_count == 0:
                    prevdata = dataobj
                    iter_count += 1
                    continue
                else:
                    try:
                        delta = prevdata - dataobj
                        
                        
                    except:
                        pass
                
                    #if delta.days > 0:
                        
                    deltas.append(delta.days)
                prevdata=dataobj
                
            try:
                
                main_delta.append(average(deltas)) # adicionando os intervalos de um 
                main_valores.append(average(valores)) # cliente a lista de intervalos gerais
            except Exception as e:
                pass
            
            if len(deltas)>=2:
                res['intervalo'] = average(deltas)
            else:
                res['intervalo'] = delta.days
            
            #iter_count += 1
            deltas.clear()
            valores.clear()
             
        
        new_res.insert(0, {"resumo": {
                            
                            "intervalo_medio":average(main_delta),
                            "valor_medio":average(main_valores),
                            } })

        return Response(new_res)         
            
        
class Intervalos(APIView):
    authentication_classes = [TokenAuthentication,]
    serializer_class = RecorrenciaSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['cliente_CPF_CNPJ', 'data']

    def get(self, request, format=None):
 
        objects = Recorrencia.objects.all()

        cpfs = []
        counter = {}
        recorrent_clients = []
        for object in objects:
            if object.cliente_CPF_CNPJ not in counter:
                counter[object.cliente_CPF_CNPJ] = 0
            counter[object.cliente_CPF_CNPJ] +=1 

        
        
        for client in counter.items():
            if int(client[1]) > 1:
                recorrent_clients.append(client[0])
            
        
        queryset = Recorrencia.objects.filter(cliente_CPF_CNPJ__in=recorrent_clients).order_by('cliente_CPF_CNPJ', '-data')
        

###########################################################
        new_res = []
        new_cli = {}

        intervalos_counter = {'De_0_a_15':0, 
                              'De_16_a_30':0, 
                              'De_31_a_45':0, 
                              'De_46_a_60':0,
                              'De_61_a_90':0,
                              'Maior_que_90':0
                              }

        for p in queryset:
            if f"<{p.cliente_CPF_CNPJ}/>" not in new_cli:
                new_cli[f"<{p.cliente_CPF_CNPJ}/>"] = []
            try:

                new_cli[f"<{p.cliente_CPF_CNPJ}/>"].append({"data":p.data.isoformat(),"valor":p.pedido_valor})    
            except:
                pass
            

        new_cli = str(new_cli)[1:-2].replace("'", '"')
        new_cli = str(new_cli).split('],')



        for n in new_cli:
            try:
                formated_string = '{'+'"cliente"'+':'+n[n.index('<')+1:n.index('/>')]+','+n+']'+'}'.replace(' ', '')
                
                formated_string = formated_string.replace(formated_string[formated_string.index('<'):formated_string.index('/>')+2], 'pedidos')
                
                new_res.append(json.loads(formated_string))
            except Exception as e:
                print(e)
                break

        client_num = 0
        format = '%Y/%m/%d'
        prevdata=datetime.datetime
        iter_count = 0
        delta = datetime.timedelta()
        deltas = []
        valores = []

        main_valores = []
        main_delta = []
        pedidos_totais = 0 # valor atualizado para compras_totais
    
        def average(days):
            soma = 0
            try:
                soma = sum(days)/len(days)    
            except:
                pass
            return soma

        for res in new_res:
            iter_count = 0   
            for data in res['pedidos']:
                dataobj = datetime.datetime.strptime(data['data'].replace('-', '/'), format)
                valor = data['valor']
                valores.append(valor)
                pedidos_totais += 1
                if iter_count == 0:
                    prevdata = dataobj
                    iter_count += 1
                    continue
                else:
                    try:
                        delta = prevdata - dataobj
                        
                        
                    except:
                        pass
                
                    #if delta.days > 0:
                    if delta.days >=0 and delta.days <= 15: 
                        intervalos_counter['De_0_a_15'] += 1
                    
                    elif delta.days >=16 and delta.days <= 30: 
                        intervalos_counter['De_16_a_30'] += 1
                    
                    elif delta.days >=31 and delta.days <= 46: 
                        intervalos_counter['De_31_a_45'] += 1
                    
                    elif delta.days >=47 and delta.days <= 61: 
                        intervalos_counter['De_46_a_60'] += 1
                    
                    elif delta.days >=62 and delta.days <= 90: 
                        intervalos_counter['De_61_a_90'] += 1
                    
                    elif delta.days > 91:
                        intervalos_counter['Maior_que_90'] += 1
                    
                   
                    deltas.append(delta.days)
                prevdata=dataobj
                
            try:
                
                main_delta.append(average(deltas)) # adicionando os intervalos de um 
                main_valores.append(average(valores)) # cliente a lista de intervalos gerais
            except Exception as e:
                pass
            
            if len(deltas)>=2:
                res['intervalo'] = average(deltas)
            else:
                res['intervalo'] = delta.days
            
            #iter_count += 1
            deltas.clear()
            valores.clear()
             
        compras_totais = intervalos_counter['De_0_a_15'] + intervalos_counter['De_16_a_30'] + intervalos_counter['De_31_a_45'] + intervalos_counter['De_46_a_60'] + intervalos_counter['De_61_a_90'] + intervalos_counter['Maior_que_90']
        new_res = []
        for p in intervalos_counter:
            print(p)
            new_res.append({'intervalo':intervalos_counter[p], 'periodo': p, 'compras_totais': compras_totais})
        
         
            
        return Response(new_res)

class BuscaIntervalo(APIView):
    authentication_classes = [TokenAuthentication,]
    serializer_class = RecorrenciaSerializer
    
    filter_backends = [filters.OrderingFilter]
    ordering = ['cliente_CPF_CNPJ', 'data']

    def get(self, request, format=None):
 
        objects = Recorrencia.objects.all()

        cpfs = []
        counter = {}
        recorrent_clients = []
        for object in objects:
                           
            if object.cliente_CPF_CNPJ not in counter:
                counter[object.cliente_CPF_CNPJ] = 0
            counter[object.cliente_CPF_CNPJ] +=1 

        page_arg = self.request.query_params.get('page', None)
        max_interval_arg = self.request.query_params.get('max-interval', None)
        min_interval_arg = self.request.query_params.get('min-interval', None)
        
        for client in counter.items():
            if int(client[1]) > 1:
                recorrent_clients.append(client[0])
            
        queryset = Recorrencia.objects.filter(cliente_CPF_CNPJ__in=recorrent_clients).order_by('cliente_CPF_CNPJ', '-data')
        
        new_res = []
        new_cli = {}

        for p in queryset:
            if f"<{p.cliente_CPF_CNPJ}/>" not in new_cli:
                new_cli[f"<{p.cliente_CPF_CNPJ}/>"] = []
            try:

                new_cli[f"<{p.cliente_CPF_CNPJ}/>"].append({"data":p.data.isoformat(),"valor":p.pedido_valor, "n_pedido":p.n_pedido})    
            except:
                pass
            

        new_cli = str(new_cli)[1:-2].replace("'", '"')
        new_cli = str(new_cli).split('],')



        for n in new_cli:
            try:
                formated_string = '{'+'"cliente"'+':'+n[n.index('<')+1:n.index('/>')]+','+n+']'+'}'.replace(' ', '')
                
                formated_string = formated_string.replace(formated_string[formated_string.index('<'):formated_string.index('/>')+2], 'pedidos')
                
                new_res.append(json.loads(formated_string))
            except Exception as e:
                print(e)
                break

        client_num = 0
        format = '%Y/%m/%d'
        prevdata=datetime.datetime
        iter_count = 0
        delta = datetime.timedelta()
        deltas = []
        valores = []

        main_valores = []
        main_delta = []
    
        def average(days):
            soma = 0
            try:
                soma = sum(days)/len(days)    
            except:
                pass
            return soma

        for res in new_res:
           
            iter_count = 0   
            for data in res['pedidos']:
                dataobj = datetime.datetime.strptime(data['data'].replace('-', '/'), format)
                valor = data['valor']
                valores.append(valor)
                if iter_count == 0:
                    prevdata = dataobj
                    iter_count += 1
                    continue
                else:
                    try:
                        delta = prevdata - dataobj
                                
                    except:
                        pass
                
                    deltas.append(delta.days)
                prevdata=dataobj
                
            try:
                main_delta.append(average(deltas)) # adicionando os intervalos de um 
                main_valores.append(average(valores)) # cliente a lista de intervalos gerais
            except Exception as e:
                pass

            res['ticket_medio'] = average(valores)

            if len(deltas)>=2:
                res['intervalo'] = average(deltas)
            else:
                res['intervalo'] = delta.days
        
            
            
            
            deltas.clear()
            valores.clear()

     

        delta = datetime.timedelta()
        deltas = []
        valores = []

        
        
        
        newnewres = []
        for caralho in new_res: 
            
            try:
                if int(caralho['intervalo']) >= int(min_interval_arg) and int(caralho['intervalo']) <= int(max_interval_arg):
                    newnewres.append(caralho)
                    deltas.append(caralho['intervalo'])
                    
                    iter_count = 0   
                    for data in caralho['pedidos']:
                        
                       
                        valores.append(data['valor'])
                

            except: 
                pass
        
        try:
            newnewres.insert(0, {"resumo": {
                                    "valor_menor":min(valores),
                                    "valor_maior":max(valores),
                                    "intervalo_maior": max(deltas),
                                    "intervalo_medio":average(deltas),
                                    "valor_medio":average(valores),
                                    "intervalo_menor":min(deltas),
                                    "total_lenght": round(len(newnewres)/100),
                                    }
                                    
                                    })
        except:
            pass
        

        if int(page_arg) == 0 or page_arg == None:
                    return Response(new_res)         
                    
        else:
            if int(page_arg)> 1:
                
                formated_res = (newnewres[(int(page_arg)*100)-99:(int(page_arg)*100)+1])
                formated_res.insert(0, newnewres[0])
                return Response(formated_res)
            else:
                return Response(newnewres[(int(page_arg)*100)-100:int(page_arg)*100])
                



class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = User.objects.get(id=token.user_id)
        userSerializer = UserSerializer(user, many=False)

        return Response({'token': token.key, 'user': userSerializer.data})