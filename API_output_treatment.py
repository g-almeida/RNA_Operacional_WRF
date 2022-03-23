# -*- coding: utf-8 -*-
'''
Treating observed data

!!! On first moment using the files provided from google drive
'''

import pandas as pd
import datetime

def leitura_dados_observados(path, sheet_name=None):
    """
    Leitura dos dados obsevados
    Aceita .xlsx e .csv

    Parameters
    ----------
    path : str, path type
        
    sheet_name : str, optional
        Mês; Ex.: "Outubro" 

    Returns
    -------
    hourly_obs_acum01 : pandas.DataFrame
        Acumulado de hora em hora observados as 00:00

    """
    if path[-4:] == 'xlsx':
        obs = pd.read_excel(path, sheet_name)
        
    else:
        obs = pd.read_csv(path)
        obs['Hora Leitura'] = pd.to_datetime(obs['Hora Leitura'])
    
    # Convertendo do fuso de Brasília para UTC (BR + 3hrs)
    obs['Hora Leitura'] = obs['Hora Leitura'].apply(lambda x: x + datetime.timedelta(hours=3)) 
    
    hourly_obs = obs.where(obs['Hora Leitura'].dt.minute==0).dropna()
    hourly_obs_acum01 = hourly_obs[['Hora Leitura', '01 h']]
    
    return hourly_obs_acum01



#   ------ Concatening provided past data downloaded from Google Drive

novembro18_maio21 = leitura_dados_observados('./files/series_Barreto 1_18-21.csv')
junho21 = leitura_dados_observados('./files/Barreto 1.xlsx', 'Junho')
julho21 = leitura_dados_observados('./files/Barreto 1.xlsx', 'Julho')
agosto21 = leitura_dados_observados('./files/Barreto 1.xlsx', 'Agosto')
setembro21 = leitura_dados_observados('./files/Barreto 1.xlsx', 'Setembro')
outubro21 = leitura_dados_observados('./files/Barreto 1.xlsx', 'Outubro')
novembro21 = leitura_dados_observados('./files/Barreto 1.xlsx', 'Novembro')

concat_list = [novembro18_maio21, junho21, julho21, agosto21, setembro21, outubro21, novembro21]

full = pd.concat(concat_list)
full.to_csv('./files/full_series_Barreto_18-21.csv')

#  ------ Bringing the API and concatening with the old files

# For this to work, we will need values for december-21, january-22, february-22. 
# Actual data until the API date, otherwise we will have dates with missing values.

from API import api_niteroi

precip_now = api_niteroi('chuva') # this returns a csv file

# next step will be to concat the dataframes ( full + precip_now )

