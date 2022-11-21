# -*- coding: utf-8 -*-
'''
Treating observed data from the API (and from google drive files (optionally))
'''

import pandas as pd
import datetime as dt
import numpy as np
import warnings
warnings.filterwarnings("ignore")

def converting_int_to_hours(val):
    """small functionality to convert int hour values to string
        used with INMET observed data
    """
    str_val = str(val).split('.')[0]
    if len(str_val) == 1:
        str_val = '0' + str_val

    hour_val = str_val + ':00:00' 
    return hour_val

def rain_values_treat(val):
    """small functionality to convert str rain values to float
        used with INMET observed data
    """
    if str(val) == 'nan':
        return np.nan 
    else:
        val = val.replace(',','.')
        return float(val)

def inmet_observed_data_reading(path, station=None):
    obs = pd.read_csv(path, sep=';')
    obs_rain = obs[["Data","Hora (UTC)","Chuva (mm)"]]

    obs_rain['Hora (UTC)'] = obs_rain['Hora (UTC)']/100
    obs_rain['Hora (UTC)'] = obs_rain['Hora (UTC)'].apply(lambda x: converting_int_to_hours(x))
    obs_rain['data'] = obs_rain['Data'] + ' ' + obs_rain['Hora (UTC)']
    obs_rain['data'] = pd.to_datetime(obs_rain['data'], format='%d/%m/%Y %H:%M:%S')

    obs_rain['Chuva (mm)'] = obs_rain['Chuva (mm)'].apply(lambda x: rain_values_treat(x))
    obs_rain['Chuva (mm)'] = obs_rain['Chuva (mm)'].interpolate()

    obs_rain.drop(['Data','Hora (UTC)'], axis=1, inplace=True)
    obs_rain.rename(columns={'Chuva (mm)': 'chuva 1h'}, inplace=True)

    return obs_rain

def observed_data_reading(path, station=None, sheet_name=None, sep=',', st_date=None, ed_date=None):
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
    
    st_date : datetime.date, 
        initial date, by default starting_date
    
    ed_date : datetime.date, 
        final date, by default ending_date

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
    obs['data'] = obs['data'].apply(lambda x: x + dt.timedelta(hours=3)) 
    obs = API_treatment(obs, station, st_date, ed_date)

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

def filling_nan_observed_data(obs_df:pd.DataFrame, st_date:dt.datetime.date, ed_date:dt.datetime.date):
    """
    Filling null data with the next day observed values.

    Parameters
    ----------
    obs_df : pd.DataFrame
        observed data
    st_date : dt.datetime.date
        initial date, by default starting_date
    ed_date : dt.datetime.date
        final date, by default ending_date
    """

    primeira_data = st_date
    ultima_data = ed_date

    # criando lista de datas que deveriam existir entre a primeira e a ultima
    datas_no_meio = []
    while primeira_data <= ultima_data:
        primeira_data = pd.to_datetime(primeira_data)
        datas_no_meio.append(primeira_data)
        primeira_data += dt.timedelta(hours=1)

    # verificando as datas no observado que nao estão na lista de datas que deveriam existir
    missing_observed_dates = []
    for date in datas_no_meio:
        if date not in obs_df['data'].unique():
            missing_observed_dates.append(date)

    # Avaliando a quantidade de datas que faltaram dados
    days_list_t = []
    for cada in missing_observed_dates:
        days_list_t.append(dt.datetime(cada.year, cada.month, cada.day))

    len_total_dates = len(obs_df['data'].dt.date.unique())
    len_missing_dates = len(pd.Series(days_list_t).unique())

    if len_missing_dates/len_total_dates > 0.2:
        return print('Abortando pois há mais de 20% de falha no dado observado')
    
    else:
        print('\n--- Em um total de: '+ str(len_total_dates) +' datas.' )
        print('\n--- Foram encontradas: '+ str(len_missing_dates) +' falhas. \nVamos preencher então com os valores observados à frente.' )

        obs_df = obs_df.set_index('data',drop=False)
        new_df = pd.DataFrame(np.nan, index=missing_observed_dates, columns=obs_df.columns)
        new_df['data'] = new_df.index
        
        joined = pd.concat([obs_df, new_df]).sort_index()
        # Premissa: Se nao sei se está chovendo, vale a chuva da hr da frente. Preferi pra rede tentar antecipar
        filled_joined = joined.fillna(method='backfill')

        return filled_joined

def API_treatment(obs_df, station=None, st_date=None, ed_date=None):
    """
    Treatment to data downloaded from API
    A) Float error specially in Barreto. Floats with two "."
        - Uses the <float_converter()> function to fix

    B) Missing_observed_data
        - Fills with data on next day

    Parameters
    ----------
    obs_df : pd.DataFrame
        observed data
    station : str, optional
        filters for the station in question, by default None
    st_date : datetime.date, 
        initial date, by default starting_date
    ed_date : datetime.date, 
        final date, by default ending_date
    Returns
    -------
    pd.DataFrame
        Station filtered and treated observed_data
    """
    if station != None:
        obs_df = obs_df.where(obs_df['estação']==station).dropna()
    
    df_values = obs_df[['chuva 15m', 'chuva 1h', 'chuva 4h', 'chuva 24h', 'chuva 96h', 'chuva 30d']]
    for cada in df_values:
        obs_df[cada] = df_values[cada].apply(lambda x: float_converter(x))
    
    obs_df = filling_nan_observed_data(obs_df=obs_df, st_date=st_date, ed_date=ed_date)
    
    return obs_df


