# -*- coding: utf-8 -*-
"""
    Script designated to treat the output of the WRF model.
        The Functions in this section are able to select the time range. And also formats each of the desired files.
"""

import os
import shutil
import datetime
import pandas as pd
from zipfile import ZipFile
import setup_reading_function as setup
import utilities as util
import WRF.WRF_output_treatment as WRF_treat
import OBS.API_output_treatment as OBS_treat
import dashboard.dashboard as dashboard
#import pickle 

# ------------------------- Functions to put data together | START -----------------------
def missing_date_finder(wrf_data, starting_date, ending_date):
  """
      Função designada para verificar os dias faltantes no WRF a partir do arquivo de dados observados.
      Note que fará o recorte baseado na lista de datas do arquivo de dados observados. Então ele funcionará como uma espécie de máscara

  Parameters:
  ----------
      wrf_data (pd.DataFrame): forecast data
      obs_data (pd.DataFrame): observed data

  Returns:
  --------
      list: Lista das datas faltantes no WRF.
  """
  wrf_data = WRF_treat.wrf_formatting(wrf_data, starting_date, ending_date)

  full_datelist = list()
  while starting_date <= ending_date:
    starting_date += datetime.timedelta(days=1)
    full_datelist.append(starting_date)

  missing_dates = []
  for cada in full_datelist:
    if cada not in list(wrf_data['Data']) and cada not in missing_dates:
        missing_dates.append(cada)
  
  return missing_dates

def filling_missing_forecast(missing_dates_list, wrf_vars, starting_date, ending_date) -> dict:
  """
      Função para preencher os dias faltantes na previsão com os dados da previsão anterior.
      
  Parameters:
  ----------
      missing_dates_list (list): forecast data
      wrf_vars (dictionary): dict of {Daily 48h WRF Forecast Data : Daily 24h WRF Forecast Data}

  Returns:
  --------
      dict: Dicionário com os valores faltantes preenchidos, cada chave é o DataFrame de uma variável atmosférica.
  """
  
  missing_dates_nb = {} # {yesterday : today}
  for today in missing_dates_list:
    yesterday = today - datetime.timedelta(days=1)
    missing_dates_nb.update({float(yesterday.strftime('%Y%m%d')) : float(today.strftime('%Y%m%d'))})


  #   ------------- Attention!!
  # 2) Replace with the forecast of day before
  # After finding the missing dates, we will create a new dataframe fillin the values with the second day on forecast

  corrected_wrf = {}

  for variable in wrf_vars.keys():
    missing_vento = wrf_vars[variable][0].where(wrf_vars[variable][0]['DATA'].isin(missing_dates_nb)).dropna() # buscando no dado completo, os dias anteriores aos faltantes
    missing_vento = missing_vento.where(missing_vento['HORA']>=25).dropna().reset_index(drop=True) # pegando desses dias anteriores, apenas as horas depois das 23 
    
    missing_vento['HORA'] = missing_vento['HORA'].apply(lambda x: x-24) # TIME CHANGE!! ***
    # !!!ATTENTION!!! : At this point variable missing_vento is with the wrong dates! Next step will adjust them!!
    for previous_forecast_date in missing_vento['DATA'].unique():
      missing_vento = missing_vento.replace(previous_forecast_date, missing_dates_nb[previous_forecast_date])
        
  
    missing_vento = WRF_treat.wrf_formatting(missing_vento, initial_date=starting_date, final_date=ending_date)

    full_wrf = WRF_treat.wrf_formatting(wrf_vars[variable][1], initial_date=starting_date, final_date=ending_date)

    variable_concat = pd.concat([missing_vento, full_wrf]).drop('Unnamed: 0', axis=1).dropna().sort_values('Datetime')

  # corrected_wrf is a dictionary with the missing values filled and each key is an atmospheric variable
    corrected_wrf.update({variable : variable_concat})
      
  return corrected_wrf

def removing_outliers(final_data):
  """
  This function removes outliers from the input data.

  Parameters:
  ----------
      final_data (pd.DataFrame)

  Returns:
  --------
      final_data (pd.DataFrame): DataFrame without outliers
  """
  print("\n--- Removing outliers ---")

  # Removing values under 0.
  str_type_columns = ['Data', 'Horario', 'Datetime']
  for col in final_data.columns:
      if col not in str_type_columns:
          # OBS.: Temperatures below 0 must be considered, so the following rule does not apply on temperature columns.
          if 'temp' not in col: 
            final_data[col] = final_data[col].apply(lambda x: float(x) if float(x) > 0 else 0)
            final_data[col] = final_data[col].apply(lambda x: 0 if float(x) > 500 else float(x))

  return final_data

# ------------------------- Functions to put data together | END -------------------------

def main(config_dict:dict, station:str):

                  ###############################################################
                  ###################### Files Selection   ######################
                      # Filters WRF data by:    
                      #     1) Station     |     2) Time_range
                  ###############################################################


  new_path, wrf_station_name = util.files_selection(station=station, config_dict=config_dict)


                  ###############################################################
                  ###################### Bringing Data  #########################
                      #     A) WRF outuput ------\
                      #                           } = Final Data.
                      #     B) OBSERVED Data ----/
                  ###############################################################
                  
  # Check the concatening studies on filtering notebook on colab from glmalmeida@id.uff.br

  # barreto is the spot variable 
  # "new_path" is the inputed path for the files before stratification

  barreto = os.listdir(new_path)
  b_prec = [] # lista dos arquivos de chuva em barreto
  b_vent = [] # lista dos arquivos de vento em barreto
  b_temp = [] # lista dos restantes
  for x in barreto:
    if 'prec' in x:
      b_prec.append(x)
    elif 'vent' in x:
      b_vent.append(x)
    else:
      b_temp.append(x)


  #vento_full = util.concatening(b_vent, new_path)
  prec_full = util.concatening(b_prec, new_path)
  temp_full = util.concatening(b_temp, new_path)

  #vento_daily = vento_full.where(vento_full['HORA']<25).dropna()
  prec_daily = prec_full.where(prec_full['HORA']<25).dropna()
  temp_daily = temp_full.where(temp_full['HORA']<25).dropna()

  #wrf_dict = {'vento': [vento_full, vento_daily], 'prec': [prec_full, prec_daily], 'temp': [temp_full, temp_daily]}
  wrf_dict = {'prec': [prec_full, prec_daily], 'temp': [temp_full, temp_daily]}

  print("\n--- |OBS| ")
  # obs_path = 'UTC_series_Barreto_18-21.csv' - config file
  
  print('   --- (OBS) Entering observed data.')
  obs_path = config_dict['Obs_Path']

  # dates input - config file
        # example: initial date=2021-08-04, final_date=2021-10-20
  print('   --- (OBS) Entering dates.')
  st_date_input_ = config_dict['Dates']['Initial_Date']
  st_date_split = st_date_input_.split('-')
  starting_date = datetime.date(int(st_date_split[0]), int(st_date_split[1]), int(st_date_split[2]))

  ed_date_input_ = config_dict['Dates']['Final_Date']
  ed_date_split = ed_date_input_.split('-')
  ending_date = datetime.date(int(ed_date_split[0]), int(ed_date_split[1]), int(st_date_split[2]))


  observed_filtered_by_date = OBS_treat.bringing_observed_data(observed_path=obs_path, st_date=starting_date, ed_date=ending_date, station=station)

                  ###############################################################
                      ################## WRF - MISSING DATES ####################
                      # 1) Look for missing data on wrf data 
                      # 2) Replace with the day before forecast
                  ###############################################################

  #   ------------- Attention!!
    # 1) Look for missing data on wrf data
  missing_dates = missing_date_finder(prec_daily, starting_date, ending_date) # this will be the missing dates

  corrected_wrf = filling_missing_forecast(missing_dates, wrf_dict, starting_date, ending_date)

                  ###############################################################
                  ########### Finally putting WRF and Observed data together ####
                  ###############################################################


  #   ------------- Finally putting WRF and Observed data together
  # *temporary* : deserves a better implementation 

  final_data = observed_filtered_by_date.drop(['Horario'],axis=1)
  final_data['Datetime'] = final_data['Datetime'].astype(str)
  
  # For unknown reason, pandas required to use pd.concat for datetime merging...
  # So, we manipulated to str
  corrected_wrf['prec'] = corrected_wrf['prec'].astype(str).drop(['Data','Horario'],axis=1)
  corrected_wrf['temp'] = corrected_wrf['temp'].astype(str).drop(['Data','Horario'],axis=1)
  
  # Setting column names:
  corrected_wrf['prec'].rename(columns={
    wrf_station_name:'prec_prev_'+ wrf_station_name,
    'Pto N':'prec_prev_ptoN',
    'Pto S':'prec_prev_ptoS',
    'Pto E':'prec_prev_ptoE',
    'Pto W':'prec_prev_ptoW',
    'Pto SE':'prec_prev_ptoSE',
    'Pto NE':'prec_prev_ptoNE',
    'Pto SW':'prec_prev_ptoSW',
    'Pto NW':'prec_prev_ptoNW'}, inplace=True)
  
  corrected_wrf['temp'].rename(columns={
    wrf_station_name:'temp_prev_'+ wrf_station_name,
    'Pto N':'temp_prev_ptoN',
    'Pto S':'temp_prev_ptoS',
    'Pto E':'temp_prev_ptoE',
    'Pto W':'temp_prev_ptoW',
    'Pto SE':'temp_prev_ptoSE',
    'Pto NE':'temp_prev_ptoNE',
    'Pto SW':'temp_prev_ptoSW',
    'Pto NW':'temp_prev_ptoNW'}, inplace=True)


  # merging precipitation
  final_data = pd.merge(final_data, corrected_wrf['prec'], on='Datetime')
  # merging temperature
  final_data = pd.merge(final_data, corrected_wrf['temp'], on='Datetime')
  # merging wind (no need to adjust colum names)
  #final_data = pd.merge(final_data, corrected_wrf['vent'], on='Datetime')
  

  # final considerantions
  final_data = removing_outliers(final_data)

                  ################################
                  ##### Exporting Final Data #####
                  ################################

  pre_input_name = config_dict['pre_input_filename'].split('.')[0] + '_' + station + '.csv'
  
  final_data.to_csv("files/inputs/pre-input/"+ pre_input_name)
  os.makedirs(new_path + "/input_files" )
  final_data.to_csv(new_path + "/input_files/" + pre_input_name)

  print("\n--- File created at: ./files/inputs/pre-input/"+ pre_input_name)

  # Removing WRF files extracted files:
  #for file in os.listdir(new_path):
 #     if file != 'input_files':
#          os.remove(new_path+file)

  # Removing extracted_files folder
  shutil.rmtree(new_path)

  print("\n--- All Done! ---")



print("""\n  ____  _   _    _              _        _    __  __ __  __  ___   ____   _   _ _____ _____ 
 |  _ \| \ | |  / \            | |      / \  |  \/  |  \/  |/ _ \ / ___| | | | |  ___|  ___|
 | |_) |  \| | / _ \    _____  | |     / _ \ | |\/| | |\/| | | | | |     | | | | |_  | |_   
 |  _ <| |\  |/ ___ \  |_____| | |___ / ___ \| |  | | |  | | |_| | |___  | |_| |  _| |  _|  
 |_| \_\_| \_/_/   \_\         |_____/_/   \_\_|  |_|_|  |_|\___/ \____|  \___/|_|   |_|    
                                                                                            """)

config_dict = setup.config_file_reading()

# Choose the desired station
station = 'Maceió'

main(config_dict=config_dict, station=station)

dashboard.launch_dashboard()