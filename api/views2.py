from .serializers import ProdutoSerializer, RecorrenciaSerializer
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import filters, status
import json
import datetime
from .order_by_client import orderByClients
from operator import itemgetter
from rest_framework.authentication import TokenAuthentication
# Create your models here.
'''
objects = Recorrencia.objects.all().order_by('data')
        
counter = {}
recorrent_clients = []
non_recorrent_clients = []
for object in objects:
    if object.cliente_CPF_CNPJ not in counter:
        counter[object.cliente_CPF_CNPJ] = 0
    counter[object.cliente_CPF_CNPJ] +=1 



for client in counter.items():
    if int(client[1]) >= 2:
        recorrent_clients.append(client[0])
    elif int(client[1]) == 1:
        non_recorrent_clients.append(client[0])



class TodosPedidos(APIView):
    authentication_classes = [TokenAuthentication,]
    def get(self, request, format=None):
        
 
        quantidade_compras = {} # contabilizar clientes que compraram x vezes
        for key in counter.keys():
            if counter[key] > 1:
                if f'c{counter[key]}' not in quantidade_compras:
                    quantidade_compras[f'c{counter[key]}'] = 0
                quantidade_compras[f'c{counter[key]}'] += 1
        
        bucetinha_gostosa = []
        for key in quantidade_compras.keys():
            bucetinha_gostosa.append(
                {
                    'quantidade_de_clientes': key.replace('c','')+' compras', #  <- tantos clientes
                    'quantidade_de_compras': int(quantidade_compras[key]) # <- compraram tantas vezes no site
                }
            )
        
        bucetinha_gostosa = sorted(bucetinha_gostosa, reverse=True, key=lambda x: (x['quantidade_de_compras']))  
        print('nao recorrentes...')
        non_recorrent_response = orderByClients(non_recorrent_clients)
        print('recorrentes...')
        recorrent_response = orderByClients(recorrent_clients)
        print('pronto!')
        
        
        response = {
            'reincidencia': bucetinha_gostosa,
            'recorrentes': recorrent_response,
            'nao_recorrentes': non_recorrent_response         
        }
        

        

        print('retornando Response')
        return Response(response, status.HTTP_200_OK)
'''   

class TodosPedidosRecorrentes(APIView):
    authentication_classes = [TokenAuthentication,]
    def get(self, request, format=None):
        data_inicial = request.GET.get('data_inicial')
        data_final = request.GET.get('data_final')

        # Converta as strings em objetos de data
        data_inicial = datetime.datetime.strptime(data_inicial, '%Y-%m-%d').date()
        data_final = datetime.datetime.strptime(data_final, '%Y-%m-%d').date()

        objects = Recorrencia.objects.all().filter(data__range=(data_inicial, data_final)).order_by('data')
        counter = {}
        recorrent_clients = []
        
        for object in objects:
            if object.cliente_CPF_CNPJ not in counter:
                counter[object.cliente_CPF_CNPJ] = 0
            counter[object.cliente_CPF_CNPJ] +=1 



        for client in counter.items():
            if int(client[1]) >= 2:
                recorrent_clients.append(client[0])
            
        
 
        quantidade_compras = {} # contabilizar clientes que compraram x vezes
        for key in counter.keys():
            if counter[key] > 1:
                if f'c{counter[key]}' not in quantidade_compras:
                    quantidade_compras[f'c{counter[key]}'] = 0
                quantidade_compras[f'c{counter[key]}'] += 1
        
        bucetinha_gostosa = []
        for key in quantidade_compras.keys():
            bucetinha_gostosa.append(
                {
                    'quantidade_de_clientes': key.replace('c','')+' compras', #  <- tantos clientes
                    'quantidade_de_compras': int(quantidade_compras[key]) # <- compraram tantas vezes no site
                }
            )
        
        bucetinha_gostosa = sorted(bucetinha_gostosa, reverse=True, key=lambda x: (x['quantidade_de_compras']))  
       
        print('recorrentes...')
        recorrent_response = orderByClients(recorrent_clients, True, data_range=(data_inicial, data_final))
        print('pronto!')
        
        
        response = {
            'reincidencia': bucetinha_gostosa,
            'recorrentes': recorrent_response,
        }
 

        return Response(response, status.HTTP_200_OK)
 

class TodosPedidosNovos(APIView):
    authentication_classes = [TokenAuthentication,]
    def get(self, request, format=None):
        data_inicial = request.GET.get('data_inicial')
        data_final = request.GET.get('data_final')

        # Converta as strings em objetos de data
        data_inicial = datetime.datetime.strptime(data_inicial, '%Y-%m-%d').date()
        data_final = datetime.datetime.strptime(data_final, '%Y-%m-%d').date()


        objects = Recorrencia.objects.all().filter(data__range=(data_inicial, data_final)).order_by('data')
        counter = {}
        
        non_recorrent_clients = []
        for object in objects:
            if object.cliente_CPF_CNPJ not in counter:
                counter[object.cliente_CPF_CNPJ] = 0
            counter[object.cliente_CPF_CNPJ] +=1 



        for client in counter.items():
        
            if int(client[1]) == 1: 
                non_recorrent_clients.append(client[0])
        quantidade_compras = {} # contabilizar clientes que compraram x vezes
        for key in counter.keys():
            if counter[key] > 1:
                if f'c{counter[key]}' not in quantidade_compras:
                    quantidade_compras[f'c{counter[key]}'] = 0
                quantidade_compras[f'c{counter[key]}'] += 1
        
        bucetinha_gostosa = []
        for key in quantidade_compras.keys():
            bucetinha_gostosa.append(
                {
                    'quantidade_de_clientes': key.replace('c','')+' compras', #  <- tantos clientes
                    'quantidade_de_compras': int(quantidade_compras[key]) # <- compraram tantas vezes no site
                }
            )
        
        bucetinha_gostosa = sorted(bucetinha_gostosa, reverse=True, key=lambda x: (x['quantidade_de_compras']))  
        non_recorrent_response = orderByClients(non_recorrent_clients, True, data_range=(data_inicial, data_final))
        response = non_recorrent_response

        print('retornando Response')
        return Response(response, status.HTTP_200_OK)


class BuscaIntervalo(APIView):
    authentication_classes = [TokenAuthentication,]
    serializer_class = RecorrenciaSerializer
    
    filter_backends = [filters.OrderingFilter]
    ordering = ['cliente_CPF_CNPJ', 'data']

    def get(self, request, format=None):
        objects = Recorrencia.objects.all().order_by('data')
        
        counter = {}
        recorrent_clients = []
        non_recorrent_clients = []
        for object in objects:
            if object.cliente_CPF_CNPJ not in counter:
                counter[object.cliente_CPF_CNPJ] = 0
            counter[object.cliente_CPF_CNPJ] +=1 



        for client in counter.items():
            if int(client[1]) >= 2:
                recorrent_clients.append(client[0])
            elif int(client[1]) == 1:
                non_recorrent_clients.append(client[0])

       
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
            except Exception as e:
                print('Erro ao inserir cliente na lista:',e)
            

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

        
        
        pedidos_filtrados = {}
        
        quantidade_clientes = 0
        for caralho in new_res: 
            
            try:
                if int(caralho['intervalo']) >= int(min_interval_arg) and int(caralho['intervalo']) <= int(max_interval_arg):
                    
                    
                    deltas.append(caralho['intervalo'])
                    quantidade_clientes += 1
                    iter_count = 0   
                    for data in caralho['pedidos']:
                        valores.append(data['valor'])
                
            except: 
                pass
        
        try:
            pedidos_filtrados = {
                        "valor_menor":min(valores),
                        "valor_maior":max(valores),
                        "intervalo_maior": max(deltas),
                        "intervalo_medio":average(deltas),
                        "valor_medio":average(valores),
                        "intervalo_menor":min(deltas),
                        "quantidade_clientes": quantidade_clientes,
                        }
                                    
                         
        except:
            return Response({'erro':'Erro ao calcular variaveis l226 views2.py, BuscaIntervalo '}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        else:
            return Response(pedidos_filtrados)
                













class Intervalos3(APIView):
    authentication_classes = [TokenAuthentication,]
    serializer_class = RecorrenciaSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['cliente_CPF_CNPJ', 'data']

    def get(self, request, format=None):
        
        classification = None
        ordering = None
        bars = None

        try:
            classification = self.request.query_params.get('classification')
            ordering = self.request.query_params.get('ordering')
            bars = int(self.request.query_params.get('bars'))
        except:
            print('request without query params.')




            
        
        queryset = Recorrencia.objects.filter(cliente_CPF_CNPJ__in=recorrent_clients).order_by('cliente_CPF_CNPJ', '-data')
        

###########################################################
        new_res = []
        new_cli = {}

        intervalos_counter = {}

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
                
                    
                   
                    
                    if f'i{delta.days}' not in intervalos_counter:
                        intervalos_counter[f'i{delta.days}'] = 0 # TODO colocar o i por tras do delta.days assim f'i{delta.days}'
                    
                    intervalos_counter[f'i{delta.days}'] += 1 # TODO colocar o i por tras do delta.days f'i{delta.days}'
                   

                    
                    
                   
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
        
        

        compras_totais = 0    
        for key in intervalos_counter.keys():
            compras_totais += intervalos_counter[key]
        
        new_res = {'compras_totais':0, 'dados':[]}
        contaod = 0
        for p in intervalos_counter:
            
            new_res['dados'].append({'ocorrencias':intervalos_counter[p], 'intervalo': int(p.replace('i','')),})
            if contaod == 0:
                print(new_res)
            contaod += 1
        
        print(new_res['dados'][0])
        if ordering == 'big2small':
            ordering = True
        elif ordering == 'small2big':
            ordering = False

        
        new_list = {'todos_os_periodos':compras_totais, 'dados': []}

        new_list['dados'] = sorted(new_res['dados'], reverse=ordering, key=lambda x: int(x[classification]))
        if classification == 'intervalo' and ordering == True:
            new_list['dados'] = new_list['dados'][1:bars+1]
            return Response(new_list)
        
        elif classification == 'ocorrencias' and ordering == False:
            new_list['dados'] = new_list['dados'][1:bars+1]
            return Response(new_list)
        
        else:
            new_list['dados'] = new_list['dados'][0:bars]
            return Response(new_list)
            

class BuscaPedidos(APIView):
    authentication_classes = [TokenAuthentication,]
    def get(self, request, format=None):
        print(self.request.user)

        valor = None
        data = None
        cliente = None
        pedido = None
        object = Recorrencia()
        response = []
        try:
            valor = self.request.query_params.get('valor')
            data = self.request.query_params.get('data')
            cliente = self.request.query_params.get('cliente')
            pedido = self.request.query_params.get('pedido')
        except:
            pass
        
        if valor is not None:
            object = Recorrencia.objects.filter(pedido_valor=valor)
        elif data is not None:
            object = Recorrencia.objects.filter(data=data)
        elif cliente is not None:
            object = Recorrencia.objects.filter(cliente_CPF_CNPJ=cliente)
        elif pedido is not None:
            object = Recorrencia.objects.filter(n_pedido=pedido)
        
        
        for o in object:

            response.append({'valor':o.pedido_valor, 'data':o.data, 'cliente':o.cliente_CPF_CNPJ, 'pedido':o.n_pedido})
        
        
        return Response(response)


def contadorProdutos(key, value, arr):
    for a in arr:
        if a[key] == value:
            a['count'] += 1
    return arr

class ProdutoDePedidos(APIView):



    def get(self, request):
        tmp_i = datetime.datetime.now()
        data_inicial = request.GET.get('data_inicial')
        data_final = request.GET.get('data_final')
        
        # Converta as strings em objetos de data
        data_inicial = datetime.datetime.strptime(data_inicial, '%Y-%m-%d').date()
        data_final = datetime.datetime.strptime(data_final, '%Y-%m-%d').date()

        pedidos = Recorrencia.objects.all().filter(data__range=(data_inicial, data_final)).order_by('data')
        counter = {}

        for pedido in pedidos:
            if f'c{pedido.cliente_CPF_CNPJ}' not in counter:
                counter[f'c{pedido.cliente_CPF_CNPJ}'] = 0
            counter[f'c{pedido.cliente_CPF_CNPJ}'] += 1
        
        counter = {key: val for key, val in counter.items() if val != 1}
        
        pedidos_recorrentes = Recorrencia.objects.filter(cliente_CPF_CNPJ__in=map(lambda cpf: cpf.replace('c',''),counter.keys()))
        produto_recorrentes = {}

        for pedido in pedidos_recorrentes:
            for produto in pedido.produtos.all():
                if produto.sku_nome not in produto_recorrentes:
                    produto_recorrentes[produto.sku_nome] = {'sku_nome': produto.sku_nome, 'sku_url':produto.sku_url, 'sku_ref':produto.sku_ref, 'count':0}
                produto_recorrentes[produto.sku_nome]['count'] += 1

        tmp_f = datetime.datetime.now() 
        print('terminado em:', tmp_f - tmp_i)  
        return Response(produto_recorrentes.items())


class ProdutoDePedidosNovos(APIView):



    def get(self, request):
        tmp_i = datetime.datetime.now()
        data_inicial = request.GET.get('data_inicial')
        data_final = request.GET.get('data_final')
        
        # Converta as strings em objetos de data
        data_inicial = datetime.datetime.strptime(data_inicial, '%Y-%m-%d').date()
        data_final = datetime.datetime.strptime(data_final, '%Y-%m-%d').date()

        pedidos = Recorrencia.objects.all().filter(data__range=(data_inicial, data_final)).order_by('data')
        counter = {}

        for pedido in pedidos:
            if f'c{pedido.cliente_CPF_CNPJ}' not in counter:
                counter[f'c{pedido.cliente_CPF_CNPJ}'] = 0
            counter[f'c{pedido.cliente_CPF_CNPJ}'] += 1
        
        counter = {key: val for key, val in counter.items() if val == 1}
        pedidos_recorrentes = Recorrencia.objects.filter(cliente_CPF_CNPJ__in=map(lambda cpf: cpf.replace('c',''),counter.keys()))
        produto_recorrentes = {}

        for pedido in pedidos_recorrentes:
            for produto in pedido.produtos.all():
                if produto.sku_nome not in produto_recorrentes:
                    produto_recorrentes[produto.sku_nome] = {'sku_nome': produto.sku_nome, 'sku_url':produto.sku_url, 'sku_ref':produto.sku_ref, 'count':0}
                produto_recorrentes[produto.sku_nome]['count'] += 1
                
        tmp_f = datetime.datetime.now() 
        print('terminado em:', tmp_f - tmp_i)  
        return Response(produto_recorrentes.items())


class ClientesView(APIView):
    def get(self, request):
        data_inicial = request.GET.get('data_inicial')
        data_final = request.GET.get('data_final')
        tipo = request.GET.get('tipo')
        orderBy = request.GET.get('orderBy')
        if orderBy == 'valor':
            orderBy = '-pedido_valor'
        pagina = int(request.GET.get('pagina'))
        # Converta as strings em objetos de data
        data_inicial = datetime.datetime.strptime(data_inicial, '%Y-%m-%d').date()
        data_final = datetime.datetime.strptime(data_final, '%Y-%m-%d').date()
        faturamento_total = 0
        
        res = {
            'generic':{
                'quantidade': 0,
                'faturamento_total':0
            },
            'clientes':[

            ]
        }

        clientes = {}
        clientes_totais = 0
        pedidos = Recorrencia.objects.all().filter(data__range=(data_inicial, data_final))
        for pedido in pedidos:
            if f'c{pedido.cliente_CPF_CNPJ}' not in clientes:
                clientes[f'c{pedido.cliente_CPF_CNPJ}'] = 0
            clientes[f'c{pedido.cliente_CPF_CNPJ}'] += 1

        if tipo == 'recorrentes':
           
            pedidos = pedidos.filter(cliente_CPF_CNPJ__in=list(map(lambda x: x[0].replace('c',''), filter(lambda x: x[1] > 1, clientes.items())))).order_by('data')
           
           
            faturamento_total = sum(map(lambda pedido: pedido.pedido_valor, pedidos))
            clientes_totais = list(map(lambda x: x[0].replace('c',''), filter(lambda x: x[1] > 1, clientes.items())))
            
        else:
           
            pedidos = pedidos.filter(cliente_CPF_CNPJ__in=list(map(lambda x: x[0].replace('c',''), filter(lambda x: x[1] == 1, clientes.items())))).order_by('data')
           
            faturamento_total = sum(map(lambda pedido: pedido.pedido_valor, pedidos))
            clientes_totais = list(map(lambda x: x[0].replace('c',''), filter(lambda x: x[1] == 1, clientes.items())))
            
     
        clientes = {}
        for pedido in pedidos:
                
            serialized = RecorrenciaSerializer(pedido).data
            serialized['produtos'] = list(map(lambda produto: ProdutoSerializer(Produto.objects.get(id=produto)).data, serialized['produtos'])) 
            cpf = serialized['cliente_CPF_CNPJ']
            if cpf not in clientes:
                clientes[cpf] = {'cpf':cpf, 'pedidos':0, 'valor_total': 0, 'datas':[], 'produtos':[]}
            clientes[cpf]['pedidos'] += 1
            clientes[cpf]['valor_total'] += serialized['pedido_valor']
            clientes[cpf]['produtos'].append({'data':serialized['data'], 'lista_produtos':serialized['produtos'][:], 'valor':serialized['pedido_valor']})
            clientes[cpf]['datas'].append(serialized['data'])
            clientes[cpf]['nome'] = serialized['nome_razao_social']
            
 
        formated_clientes = list(clientes.values())
        if orderBy == 'pedidos':
            formated_clientes = list(sorted(formated_clientes, key=lambda cliente: cliente['pedidos'], reverse=True))
        else:
            formated_clientes = list(sorted(formated_clientes, key=lambda cliente: cliente['valor_total'], reverse=True))
        res['generic']['faturamento_total'] = faturamento_total
        res['generic']['quantidade'] = len(clientes_totais)
        res['clientes'] = formated_clientes[(pagina-1)*20:pagina*20]

      
 
        return(Response(res))