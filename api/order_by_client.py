from .serializers import RecorrenciaSerializer
from .models import Recorrencia
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import filters
import json
import datetime


def orderByClients(clients, filter=False, data_range=()):
        queryset = Recorrencia
        if filter:   
            queryset = Recorrencia.objects.filter(data__range=data_range).filter(cliente_CPF_CNPJ__in=clients).order_by('cliente_CPF_CNPJ', '-data')
        else:
            queryset = Recorrencia.objects.filter(cliente_CPF_CNPJ__in=clients).order_by('cliente_CPF_CNPJ', '-data')

        data_ultimo_pedido = Recorrencia.objects.latest('data').data
        
      
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

        total_pedidos = len(clients)
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

        

        new_res =  {
                    "data_ultimo_pedido":data_ultimo_pedido,
                    "valor_menor":min(main_valores),
                    "valor_maior":max(main_valores) ,
                    "intervalo_maior": max(main_delta),
                    "intervalo_medio":average(main_delta),
                    "valor_medio":average(main_valores),
                    "intervalo_menor": min(main_delta),
                    "quantidade_clientes": total_pedidos
                    }
                    
                
        main_delta.remove(0)
        new_res["intervalo_menor"] = min(main_delta)
        
        
    
        return new_res