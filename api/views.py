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
             
        compras_totais = len(new_res)
        new_res = []
        for p in intervalos_counter:
            new_res.append({'intervalo':intervalos_counter[p], 'periodo': p, 'compras_totais': compras_totais})
        
         
            
        return Response(new_res)

class BuscaIntervalo(APIView):
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
                
