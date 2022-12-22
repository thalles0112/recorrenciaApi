from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import RecorrenciaSerializer
from .models import Recorrencia
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import filters
import json
import datetime

      
class PedidosClientes(APIView):
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
        limit_arg = self.request.query_params.get('limiter', None)
        
        for client in counter.items():
            if int(client[1]) > 1:
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
                else:
                    try:
                        if prevdata != dataobj:
                            delta = prevdata - dataobj
                        else:
                            pass
                        
                        
                    except:
                        pass
                
                    if delta.days > 0:
                        
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
                            "valor_menor":min(main_valores),
                            "valor_maior":max(main_valores) ,
                            "intervalo_maior": max(main_delta),
                            "intervalo_medio":average(main_delta),
                            
                            "valor_medio":average(main_valores),
                            "intervalo_menor": min(main_delta)
                            }
                            
                            })
        main_delta.remove(0)
        new_res[0]["resumo"]["intervalo_menor"] = min(main_delta)
        
        
        #calculando a media dos intervalos e inserindo na lista que
        # vai ser retornada à api

        if int(limit_arg) == 0:
            return Response(new_res)         
            
        else:
            return Response(new_res[:int(limit_arg)])

    
             

class NaoRecorrente(APIView):
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
        limit_arg = self.request.query_params.get('limiter', None)
        
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
            "valor_maior":max(main_valores)
                }
            
            })
        #calculando a media dos intervalos e inserindo na lista que
        # vai ser retornada à api

        if int(limit_arg) == 0: 
            return Response(new_res)         
            
        else:
            return Response(new_res[:int(limit_arg)])