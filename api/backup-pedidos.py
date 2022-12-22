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
        limit_arg = self.request.query_params.get('limit', None)
        
        for client in counter.items():
            if client[1] > 1:
                recorrent_clients.append(client[0])
            
        if cpf_arg is not None:

            queryset = Recorrencia.objects.filter(cliente_CPF_CNPJ=cpf_arg)
        else:
            recorrent_clients.append(cpf_arg)
            queryset = Recorrencia.objects.filter(cliente_CPF_CNPJ__in=recorrent_clients)
        

###########################################################
        new_res = []
        new_cli = {}

        

        for p in queryset:
            if f"{p.cliente_CPF_CNPJ}" not in new_cli:
                new_cli[f"{p.cliente_CPF_CNPJ}"] = []
            try:

                new_cli[f"{p.cliente_CPF_CNPJ}"].append({"data":p.data.isoformat(),"valor":p.pedido_valor})    
            except:
                pass
            

        new_cli = str(new_cli)[1:-2].replace("'", '"')
        new_cli = str(new_cli).split('],')



        for n in new_cli:
            try:
                caralho = '{'+n+']'+'}'.replace(' ', '')
                new_res.append(json.loads(caralho))
            except Exception as e:
                print(e)

        client_num = 0

        
        if limit_arg is not None:
            
            return Response(new_res[:int(limit_arg)])
        else:
            return Response(new_res)
        
    

        