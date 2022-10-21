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
from API_output_treatment import inmet_observed_data_reading

def files_date_filter(start_date, end_date, spot_list):
    '''
    Filters data for starting and ending dates.
    '''
    b_prec = [] # lista dos arquivos de chuva em barreto
    b_vent = [] # lista dos arquivos de vento em barreto
    others = [] # lista dos restantes
    for x in spot_list:
      if 'prec' in x:
        b_prec.append(x)
      elif 'vent' in x:
        b_vent.append(x)
      else:
        others.append(x)

    datefilter=[]
    while start_date <= end_date:
      datestr = start_date.strftime("%Y-%m-%d").replace('-','')
      
      for cada in others:
        if datestr in cada:
          datefilter.append(cada)      
      for cada in b_prec:
        if datestr in cada:
          datefilter.append(cada)    
      for cada in b_vent:
        if datestr in cada:
          datefilter.append(cada)  

      start_date+=datetime.timedelta(days=1)

    return datefilter


#  -----------   Files treatment

def adaptingTXT(path):
  data = pd.read_csv(path, sep='\s+')
  pt_cols=['DATA', 'HORA','Barreto','Pto N','Pto S','Pto E','Pto W','Pto SE','Pto NE','Pto SW','Pto NW']
  vent_cols=['DATA',    'HORA',     'Barreto_ws10', 'Barreto_wd10', 'Pto N_ws10',   'Pto N_wd10',   'Pto S_ws10',   'Pto S_wd10',   'Pto E_ws10',   'Pto E_wd10',   'Pto W_ws10',   'Pto W_wd10',   'Pto SE_ws10',  'Pto SE_wd10' , 'Pto NE_ws10' , 'Pto NE_wd10'  ,'Pto SW_ws10'  ,'Pto SW_wd10','Pto NW_ws10', 'Pto NW_wd10']

  try:
    data.drop(['Pto.8', 'SE_ws10', 'Pto.9', 'SE_wd10', 'Pto.10', 'NE_ws10', 'Pto.11',
       'NE_wd10', 'Pto.12', 'SW_ws10', 'Pto.13', 'SW_wd10', 'Pto.14',
       'NW_ws10', 'Pto.15', 'NW_wd10'], axis=1, inplace=True)
    data.columns=vent_cols
  except:
    data.drop(['Pto.4', 'SE', 'Pto.5', 'NE', 'Pto.6', 'SW', 'Pto.7','NW'], axis=1, inplace=True)
    data.columns=pt_cols
  
  return data




#                 ------- Barreto's October case

#     Data will be unzipped from extrai_rna.zip to ./files/extrai_rna/ and then filtered for the october month
#     The files will be renamed to the format: 'Barreto_YYYYMMDD.txt'
#     The filtered files will be moved to the folder ./files/OctoberWRF/

config_dict = setup.config_file_reading()

print("\n--- Creating directory for extraction of the files.")
#new_extraction_path = input('Enter the dir name for new extraction folder: ')
new_extraction_path = config_dict['New_Dir']

try:
  october_path = './files/' + new_extraction_path + '/'
  os.makedirs(october_path)
except:
  print('\n---ERROR! Folder already exists')
  exit()

# Entering WRF files
print("\n--- Entering WRF files.")
# entering the wrf zip file: Ex: 'extrai_rn.zip'
#wrf_zip = input('Enter the name of the wrf compressed folder. \n (Usually "extrai_rn.zip")')
wrf_zip_path = config_dict['zip_file_path']

# WRF files entries options:
# 1 - Zip package
# 2 - Existing Folder

if ".zip" in wrf_zip_path:  # 1 - Zip package
  print("\n--- Unzipping the files.")

  destination_path = "./files/"
  temp_zip_path = destination_path + "extrai_rn/" # OBS.: this is necessary because the unzip creates a folder with its name
  #os.makedirs(destination_path)

  with ZipFile(wrf_zip_path, 'r') as zipObj:
    zipObj.extractall(destination_path)

  print('\n--- Files unzipped')

else:  # 2 - Existing Folder
  temp_zip_path = wrf_zip_path + '/'
  print('\n--- Moving the files.')


# Filtering Barreto files. NEXT STEP!!
files = os.listdir(temp_zip_path)
barreto_list = []
for cada in files:
  if 'Barreto' in cada and 'Zone' not in cada: 
    barreto_list.append(cada)

# Filtering files by selected timerange
# This will move from temporary after extraction folder to the instance WRF files folder.
datefilter_start_split = config_dict['Dates']['Initial_Date'].split('-')
datefilter_start = datetime.date(int(datefilter_start_split[0]), int(datefilter_start_split[1]), int(datefilter_start_split[2]))
datefilter_end_split = config_dict['Dates']['Final_Date'].split('-')
datefilter_end = datetime.date(int(datefilter_end_split[0]), int(datefilter_end_split[1]), int(datefilter_end_split[2]))
datefilter = files_date_filter(datefilter_start, datefilter_end, barreto_list)

# Moving the filtered files to the folder ./files/OctoberWRF/
#try:
for file in files:
  if file in datefilter:
    # First path is the WRF provided data
    # Second path is the destination path for the filtered data (station and date)
    print('moving ' + temp_zip_path+file + 'to' + october_path)
    shutil.copy(temp_zip_path+ file, october_path)
#except:
#  print('\n--- The files have been filtered.')


# treatment for each file on ./file/OctoberWRF
for cada in os.listdir(october_path):
  path2 = october_path+cada
  #path2)
  csv = adaptingTXT(path2)
  print('transforming ' + path2 +"to" + october_path + cada[:-3]+'.csv')
  csv.to_csv(october_path+cada[:-3]+'csv')
  os.remove(path2)

if ".zip" in wrf_zip_path:
  shutil.rmtree(temp_zip_path)
  print('\n--- Removing the temporary extracted folder.')


# Check the concatening stuff on filtering notebook on colab from glmalmeida@id.uff.br


                  #  -----------   Files treatment (Concatenation)

# barreto is the spot variable 
# october path is the inputed path for the files before stratification

barreto = os.listdir(october_path)
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


def concatening(lista, path):
  to_concat = []
  for cada in lista:
    to_concat.append(pd.read_csv(path+cada))

  return pd.concat(to_concat)

vento_full = concatening(b_vent, october_path)
prec_full = concatening(b_prec, october_path)
temp_full = concatening(b_temp, october_path)

vento_daily = vento_full.where(vento_full['HORA']<25).dropna()
prec_daily = prec_full.where(prec_full['HORA']<25).dropna()
temp_daily = temp_full.where(temp_full['HORA']<25).dropna()

wrf_dict = {'vento': [vento_full, vento_daily], 'prec': [prec_full, prec_daily], 'temp': [temp_full, temp_daily]}

def wrf_formatting(wrf_data, initial_date, final_date):

  wrf_data = wrf_data.reset_index(drop=True)

  wrf_data['Data'] = wrf_data['DATA'].apply(lambda x: datetime.date(int(str(x)[:4]), int(str(x)[4:6]), int(str(x)[6:8])))
  wrf_data['Horario'] = wrf_data['HORA'].apply(lambda x: datetime.time(int(x-1)))  

  # !!!!!  HORA DO ARQUIVO ORIGINAL FOI SUBTRAÍDA POR 1 !!!!!'
  # ASSUMIU-SE QUE O ARQUIVO ORIGINAL FOI FEITO COM A MÉDIA DA 1 HORA, 2 HORA E ...'
  wrf_data['DATA-HORA'] = wrf_data['Data'].astype(str) + ' ' + wrf_data['Horario'].astype(str)
  wrf_data['Datetime'] = wrf_data['DATA-HORA'].apply(lambda x: datetime.datetime(int(x[:4]), int(x[5:7]), int(x[8:10]), int(x.split(' ')[1].split(':')[0])))
  
  wrf_data = wrf_data.drop(['DATA', 'HORA', 'DATA-HORA'], axis=1)

  wrf_data = wrf_data.where((wrf_data['Data']>=initial_date) & (wrf_data['Data']<=final_date)).dropna()
  
  wrf_data = wrf_data.sort_values('Datetime')

  return wrf_data

#   -------------  Observed data treatment

# obs_path = 'UTC_series_Barreto_18-21.csv' - config file
print('\n--- Entering observed data.')
#obs_path = input('Enter the file name of the observed data: \n Usually "UTC_series_Barreto_18-21.csv" ')
obs_path = config_dict['Obs_Path']
#obs = pd.read_csv(obs_path).drop('Unnamed: 0', axis=1)
#obs = obs.rename(columns={'Hora Leitura': 'Data', '01 h':'precipitacao_observada'})
obs = inmet_observed_data_reading(obs_path, station='Barreto 1') # NEXT STEP!!
obs = obs.rename(columns={'data': 'Data', 'chuva 1h':'precipitacao_observada'})
obs = obs.sort_values('Data')
obs['Horario'] = obs['Data'].astype('datetime64[ns]').dt.time

obs['Data'] = obs['Data'].astype('datetime64[ns]').dt.date


obs['DATA-HORA'] = obs['Data'].astype(str) + ' ' + obs['Horario'].astype(str)
obs['Datetime'] = obs['DATA-HORA'].apply(lambda x: datetime.datetime(int(x[:4]), int(x[5:7]), int(x[8:10]), int(x.split(' ')[1].split(':')[0])))
obs = obs.drop('DATA-HORA', axis=1)
obs.sort_values('Datetime', inplace=True)


    # dates input - config file
      # example: initial date=2021-08-04, final_date=2021-10-20
print('\n--- Entering dates.')
#st_date_input_ = input('Enter the initial date for observed data (yyyy-mm-dd): ')
st_date_input_ = config_dict['Dates']['Initial_Date']
st_date_split = st_date_input_.split('-')
starting_date = datetime.date(int(st_date_split[0]), int(st_date_split[1]), int(st_date_split[2]))


#ed_date_input_ = input('Enter the final date for observed data (yyyy-mm-dd): ')
ed_date_input_ = config_dict['Dates']['Final_Date']
ed_date_split = ed_date_input_.split('-')
ending_date = datetime.date(int(ed_date_split[0]), int(ed_date_split[1]), int(st_date_split[2]))


observed_filtered_by_date = obs.where((obs['Data']>=starting_date) & (obs['Data']<=ending_date)).dropna()


                ###############################################################
                    ################## WRF - MISSING DATES ####################
                    # 1) Look for missing data on wrf data 
                    # 2) Replace with the day before forecast
                ###############################################################

def missing_date_finder(wrf_data, obs_data):
  """Função designada para verificar os dias faltantes no WRF a partir do arquivo de dados observados.
      Note que fará o recorte baseado na lista de datas do arquivo de dados observados. Então ele funcionará como uma espécie de máscara

  Args:
      wrf_data (pd.DataFrame): [description]
      obs_data (pd.DataFrame): [description]

  Returns:
      list: Lista das datas faltantes no WRF.
  """
  initial_date = obs_data.sort_values('Datetime')['Datetime'].iloc[0]
  final_date = obs_data.sort_values('Datetime')['Datetime'].iloc[-1]

  wrf_data = wrf_formatting(wrf_data, initial_date, final_date)

  missing_dates = []
  for cada in list(obs_data['Data']):
    if cada not in list(wrf_data['Data']) and cada not in missing_dates:
        missing_dates.append(cada)
        
  return missing_dates


#   ------------- Attention!!
  # 1) Look for missing data on wrf data

missing_dates = missing_date_finder(vento_daily, observed_filtered_by_date) # this will be the missing dates
missing_dates_nb = {} # {yesterday : today}

for today in missing_dates:
  yesterday = today - datetime.timedelta(days=1)
  missing_dates_nb.update({float(yesterday.strftime('%Y%m%d')) : float(today.strftime('%Y%m%d'))})


#   ------------- Attention!!
  # 2) Replace with the day before forecast
  # After finding the missing dates, we will create a new dataframe fillin the values with the second day on forecast

corrected_wrf = {}
for variable in wrf_dict:
  missing_vento = wrf_dict[variable][0].where(wrf_dict[variable][0]['DATA'].isin(missing_dates_nb)).dropna() # buscando no dado completo, os dias anteriores aos faltantes
  missing_vento = missing_vento.where(missing_vento['HORA']>=25).dropna().reset_index(drop=True) # pegando desses dias anteriores, apenas as horas depois das 23 
  missing_vento['HORA'] = missing_vento['HORA'].apply(lambda x: x-24) # ajustando os horários

  for cada in missing_dates_nb:
      missing_vento = missing_vento.replace(cada, missing_dates_nb[cada])
  missing_vento = wrf_formatting(missing_vento, initial_date=starting_date, final_date=ending_date)

  full_wrf = wrf_formatting(wrf_dict[variable][1], initial_date=starting_date, final_date=ending_date)

  variable_concat = pd.concat([missing_vento, full_wrf]).drop('Unnamed: 0', axis=1).dropna().sort_values('Datetime')

# corrected_wrf is a dictionary with the missing values filled and each key is an atmospheric variable
  corrected_wrf.update({variable : variable_concat})


                ###############################################################
                ########### Finally putting WRF and Observed data together ####
                ###############################################################

#   ------------- Finally putting WRF and Observed data together
# *temporary* : deserves a better implementation 
final_data = observed_filtered_by_date

final_data['Barreto_ws10']=corrected_wrf['vento']['Barreto_ws10'].values
final_data['Barreto_wd10']=corrected_wrf['vento']['Barreto_wd10'].values
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


final_data['prec_prev_Barreto']=corrected_wrf['prec']['Barreto'].values
final_data['prec_prev_ptoN']=corrected_wrf['prec']['Pto N'].values
final_data['prec_prev_ptoS']=corrected_wrf['prec']['Pto S'].values
final_data['prec_prev_ptoE']=corrected_wrf['prec']['Pto E'].values
final_data['prec_prev_ptoW']=corrected_wrf['prec']['Pto W'].values
final_data['prec_prev_ptoSE']=corrected_wrf['prec']['Pto SE'].values
final_data['prec_prev_ptoNE']=corrected_wrf['prec']['Pto NE'].values
final_data['prec_prev_ptoSW']=corrected_wrf['prec']['Pto SW'].values
final_data['prec_prev_ptoNW']=corrected_wrf['prec']['Pto NW'].values

final_data['temp_prev_Barreto']=corrected_wrf['temp']['Barreto'].values
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


# pre_input_name format example: 'UTC_AugOut_WRF_obs.csv''  - config file
#pre_input_name = input("All done! \n\nPlease, enter the name of the file you want to save the data: \n (Format example: 'UTC_AugOut_WRF_obs.csv'")
pre_input_name = config_dict['pre_input_filename']
final_data.to_csv("./files/inputs/pre-input/"+ pre_input_name)
os.makedirs(october_path + "/input_files" )
final_data.to_csv(october_path + "/input_files/" + pre_input_name)
print("\n--- File created at: ./files/inputs/pre-input/"+ pre_input_name)
print("\n--- All Done! ---")