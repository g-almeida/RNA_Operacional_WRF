# -*- coding: utf-8 -*-
'''
Treating observed data from the API (and from google drive files (optionally))
'''

import pandas as pd
import datetime

def observed_data_reading(path, station=None, sheet_name=None, sep=','):
    """
    Observed data reading and UTC conversion.
    The file expected for input is the 'hourly_data.csv' wich is being concatenated on lab server.

    Optionally also treats the excel files earlyer downloaded from google drive.
    
    So: works with .xlsx e .csv

    Parameters
    ----------
    path : str, path to .csv or .xlsx file
        
    station : str, station name
        Ex.: "Barreto 1"

    sheet_name : str, optional
        If the file is an excel file, the sheet name to be read.
        Mês; Ex.: "Outubro" 

    Returns
    -------
    hourly_obs_acum01 : pandas.DataFrame
        Station hourly accumulated data verified at 00:00:00.

    """
    if station==None:
        print("\n\n ! ERROR ! \nPlease select a station! \nThis function will return its accumulated data.")
        return 

    if path[-4:] == 'xlsx':
        obs = pd.read_excel(path, sheet_name)

        # -------- Excel sheets provided has another format, so we need to change the columns names
        obs = obs.rename(columns={'Hora Leitura':'data', '01 h':'chuva 1h'})
        
    else:
        # -------- Read the csv file provided from the API (Here column names already comes with the right name)
        obs = pd.read_csv(path, sep=sep)
        
    # Convertendo do fuso de Brasília para UTC (BR + 3hrs)
    obs['data'] = pd.to_datetime(obs['data'], infer_datetime_format=True)
    obs['data'] = obs['data'].apply(lambda x: x + datetime.timedelta(hours=3)) 
    obs = API_treatment(obs, station)


    hourly_obs = obs.where(obs['data'].dt.minute==0).dropna()
    hourly_obs_acum01 = hourly_obs[['data', 'chuva 1h']]
    
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
    ''' Treatment to data downloaded from API
        Float error specially in Barreto. Floats with two "."
        Uses the <float_converter()> function to fix
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

