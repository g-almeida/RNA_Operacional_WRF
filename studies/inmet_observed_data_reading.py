import pandas as pd
import numpy as np

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