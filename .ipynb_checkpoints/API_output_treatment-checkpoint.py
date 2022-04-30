# -*- coding: utf-8 -*-
'''
Treating observed data

!!! On first moment using the files provided from google drive.
'''

import pandas as pd
import datetime

def leitura_dados_observados_prefeitura(path, sheet_name=None):
    """
    Leitura dos dados obsevados passados pela prefeitura
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
    
    # Renomeando pros nossos padrões
    hourly_obs_acum01 = hourly_obs_acum01.rename(columns={'Hora Leitura':'data', '01 h':'chuva 1h'})
    
    return hourly_obs_acum01

def float_converter(one):
    ''' Some precipitation values are coming with the '0.0.1' format, so this function
        drops the last '.' and converts the value to float type.
        
    '''
    try:
        fixed_float = float(one)
    except:
        separ = one.split('.')
        comma = one.split('.')[0]+'.'
        fixed_float = float(comma+''.join(one.split('.')[1:]))
        
    return fixed_float

def API_treatment(obs_df, station=None):
    ''' Treatment designated to data downloaded from API
    '''
    if station != None:
        obs_df = obs_df.where(obs_df['estação']==station).dropna()
    
    
    df_values = obs_df[['chuva 15m', 'chuva 1h', 'chuva 4h', 'chuva 24h', 'chuva 96h', 'chuva 30d']]
    for cada in df_values:
        obs_df[cada] = df_values[cada].apply(lambda x: float_converter(x))
    
    return obs_df
#   ------ Concatening provided past data downloaded from Google Drive
'''
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
'''
#  ------ Bringing the API and concatening with the old files

# For this to work, we will need values for december-21, january-22, february-22. 
# Actual data until the API date, otherwise we will have dates with missing values.
'''
from API import api_niteroi

precip_now = api_niteroi('chuva') # this returns a dataframe
'''
# next step will be to concat the dataframes ( full + precip_now )

