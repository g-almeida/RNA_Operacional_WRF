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
#from API_output_treatment import observed_data_reading
import utilities as util
import WRF.WRF_output_treatment as WRF_treat
import OBS.observed_data_treatment as OBS_treat
import dashboard.dashboard as dashboard

# ------------------------- Functions to put data together | START -----------------------
def missing_date_finder(wrf_data, obs_data):
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
  initial_date = obs_data.sort_values('Datetime')['Datetime'].iloc[0]
  final_date = obs_data.sort_values('Datetime')['Datetime'].iloc[-1]

  wrf_data = WRF_treat.wrf_formatting(wrf_data, initial_date, final_date)

  missing_dates = []
  for cada in list(obs_data['Data']):
    if cada not in list(wrf_data['Data']) and cada not in missing_dates:
        missing_dates.append(cada)
        
  return missing_dates

def filling_missing_forecast(missing_dates_list, wrf_vars, starting_date, ending_date) -> dict:
  """
      Função para preencher os dias faltantes na previsão.

  Parameters:
  ----------
      missing_dates_list (list): forecast data
      wrf_vars (dictionary): dict of {Daily 48h WRF Forecast Data : Daily 24h WRF Forecast Data}

  Returns:
  --------
      dict: Dicionário com os valores faltantes preenchidos e cada chave é uma variável atmosférica.
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
    missing_vento['HORA'] = missing_vento['HORA'].apply(lambda x: x-24) # ajustando os horários

    for cada in missing_dates_nb:
        missing_vento = missing_vento.replace(cada, missing_dates_nb[cada])
    missing_vento = WRF_treat.wrf_formatting(missing_vento, initial_date=starting_date, final_date=ending_date)

    full_wrf = WRF_treat.wrf_formatting(wrf_vars[variable][1], initial_date=starting_date, final_date=ending_date)

    variable_concat = pd.concat([missing_vento, full_wrf]).drop('Unnamed: 0', axis=1).dropna().sort_values('Datetime')

  # corrected_wrf is a dictionary with the missing values filled and each key is an atmospheric variable
    corrected_wrf.update({variable : variable_concat})
      
  return corrected_wrf

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


  vento_full = util.concatening(b_vent, new_path)
  prec_full = util.concatening(b_prec, new_path)
  temp_full = util.concatening(b_temp, new_path)

  vento_daily = vento_full.where(vento_full['HORA']<25).dropna()
  prec_daily = prec_full.where(prec_full['HORA']<25).dropna()
  temp_daily = temp_full.where(temp_full['HORA']<25).dropna()

  wrf_dict = {'vento': [vento_full, vento_daily], 'prec': [prec_full, prec_daily], 'temp': [temp_full, temp_daily]}


  # obs_path = 'UTC_series_Barreto_18-21.csv' - config file
  print('\n--- Entering observed data.')
  obs_path = config_dict['Obs_Path']

  # dates input - config file
        # example: initial date=2021-08-04, final_date=2021-10-20
  print('\n--- Entering dates.')
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


  missing_dates = missing_date_finder(vento_daily, observed_filtered_by_date) # this will be the missing dates

  corrected_wrf = filling_missing_forecast(missing_dates, wrf_dict, starting_date, ending_date)


                  ###############################################################
                  ########### Finally putting WRF and Observed data together ####
                  ###############################################################


  #   ------------- Finally putting WRF and Observed data together
  # *temporary* : deserves a better implementation 
  final_data = observed_filtered_by_date

  final_data[wrf_station_name +'_ws10']=corrected_wrf['vento'][wrf_station_name +'_ws10'].values
  final_data[wrf_station_name +'_wd10']=corrected_wrf['vento'][wrf_station_name +'_wd10'].values
  final_data['Pto N_ws10']=corrected_wrf['vento']['Pto N_ws10'].values
  final_data['Pto N_wd10']=corrected_wrf['vento']['Pto N_wd10'].values
  final_data['Pto S_ws10']=corrected_wrf['vento']['Pto S_ws10'].values
  final_data['Pto S_wd10']=corrected_wrf['vento']['Pto S_wd10'].values
  final_data['Pto E_ws10']=corrected_wrf['vento']['Pto E_ws10'].values
  final_data['Pto E_wd10']=corrected_wrf['vento']['Pto E_wd10'].values
  final_data['Pto W_ws10']=corrected_wrf['vento']['Pto W_ws10'].values
  final_data['Pto W_wd10']=corrected_wrf['vento']['Pto W_wd10'].values
  final_data['Pto SE_ws10']=corrected_wrf['vento']['Pto SE_ws10'].values
  final_data['Pto SE_wd10']=corrected_wrf['vento']['Pto SE_wd10'].values
  final_data['Pto NE_ws10']=corrected_wrf['vento']['Pto NE_ws10'].values
  final_data['Pto NE_wd10']=corrected_wrf['vento']['Pto NE_wd10'].values
  final_data['Pto SW_ws10']=corrected_wrf['vento']['Pto SW_ws10'].values
  final_data['Pto SW_wd10']=corrected_wrf['vento']['Pto SW_wd10'].values
  final_data['Pto NW_ws10']=corrected_wrf['vento']['Pto NW_ws10'].values
  final_data['Pto NW_wd10']=corrected_wrf['vento']['Pto NW_wd10'].values

  final_data['prec_prev_'+ wrf_station_name]=corrected_wrf['prec'][wrf_station_name].values
  final_data['prec_prev_ptoN']=corrected_wrf['prec']['Pto N'].values
  final_data['prec_prev_ptoS']=corrected_wrf['prec']['Pto S'].values
  final_data['prec_prev_ptoE']=corrected_wrf['prec']['Pto E'].values
  final_data['prec_prev_ptoW']=corrected_wrf['prec']['Pto W'].values
  final_data['prec_prev_ptoSE']=corrected_wrf['prec']['Pto SE'].values
  final_data['prec_prev_ptoNE']=corrected_wrf['prec']['Pto NE'].values
  final_data['prec_prev_ptoSW']=corrected_wrf['prec']['Pto SW'].values
  final_data['prec_prev_ptoNW']=corrected_wrf['prec']['Pto NW'].values

  final_data['temp_prev_'+ wrf_station_name]=corrected_wrf['temp'][wrf_station_name].values
  final_data['temp_prev_ptoN']=corrected_wrf['temp']['Pto N'].values
  final_data['temp_prev_ptoS']=corrected_wrf['temp']['Pto S'].values
  final_data['temp_prev_ptoE']=corrected_wrf['temp']['Pto E'].values
  final_data['temp_prev_ptoW']=corrected_wrf['temp']['Pto W'].values
  final_data['temp_prev_ptoSE']=corrected_wrf['temp']['Pto SE'].values
  final_data['temp_prev_ptoNE']=corrected_wrf['temp']['Pto NE'].values
  final_data['temp_prev_ptoSW']=corrected_wrf['temp']['Pto SW'].values
  final_data['temp_prev_ptoNW']=corrected_wrf['temp']['Pto NW'].values


                  ################################
                  ##### Final Considerations #####
                  ################################

  # Removing values under 0.
  str_type_columns = ['Data', 'Horario', 'Datetime']
  for col in final_data.columns:
      if col not in str_type_columns:
          # OBS.: Temperatures below 0 must be considered, so the following rule does not apply on temperature columns.
          if 'temp' not in col: 
            final_data[col] = final_data[col].apply(lambda x: float(x) if float(x) > 0 else 0)

  pre_input_name = config_dict['pre_input_filename'].split('.')[0] + '_' + station + '.csv'
  final_data.to_csv("./files/inputs/pre-input/"+ pre_input_name)
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
station = 'Pé Pequeno'

main(config_dict=config_dict, station=station)

dashboard.launch_dashboard()