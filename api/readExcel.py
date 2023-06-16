import os
import pandas as pd
import json
import datetime

def format_data(json_sequence):
    #print('formatando data')
    for value in json_sequence:
        try:
            value['data'] = datetime.datetime.strptime(value['data'][0:10], '%d/%m/%Y').strftime('%Y/%m/%d')
        except:
            pass
    return json_sequence

def format_number(json_sequence=[{},{}]):
    #print('formatando numeros')
    keys = json_sequence[0].keys()
    formated_sequence = []
    for dic in json_sequence:    
        for key in dic:
            try:
                dic[key] = dic[key].replace('.','').replace(',','.')
                if 'R$' in dic[key]:
                    dic[key] = dic[key].replace('R$','').strip()
                elif '%' in dic[key]:
                    dic[key] = dic[key].replace('%','').strip()
                elif '-' in dic[key]:
                    dic[key] = '0'
                elif dic[key] is null:
                    dic[key] = '0'
                elif dic[key] is null:
                    dic[key] = '0'
                elif dic[key] is None:
                    dic[key] = '0'
            except:
                pass

    return json_sequence       

  

def excel2peewee_data_formatter(excel_file_path, sheet): # retorna um dicionario da leitura do excel 
    '''
    helper function. returns formated data to use with peewee.insertMany()
    '''
    plan = pd.read_excel(excel_file_path, sheet)

    values = []
    data = {}

    for k in plan.keys(): # mapear todas as colunas
        for i in plan[k]: # mapear todas linhas da coluna atual
            values.append(i) # inserir esses dados numa lista temporaria
     

        data[k] = values[:] # inserir os dados da lista temporaria no dicionario principaç
        values.clear() # limpar dados da lista temporaria
    

    # até aqui foram lidos os dados e armazenados em um dicionario
    #======================================#
    # aqui será gerada a sequencia compativel com o metodo insert_many() do peewee (tictac)
    tmp_dict = {}
    tmp_list = []
    key_list = []
    va_list  = []

    idx = 0

    for va in data.values():
        va_list.append(va)

    for ke in data.keys():
        key_list.append(ke)


    for v in range(len(va_list[0])):

        for k in key_list:
            tmp_dict[k] = va_list[idx][v]
            
            idx += 1
        idx = 0
        tmp_list.append(tmp_dict.copy())
        tmp_dict.clear()
    
    return tmp_list



