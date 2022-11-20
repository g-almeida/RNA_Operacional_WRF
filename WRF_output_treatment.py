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
from API_output_treatment import observed_data_reading

#  -----------   Files treatment Utilities

def files_date_filter(start_date, end_date, spot_list) -> list:     # Util
  """Filters data for starting and ending dates.

  Parameters
  ----------
  start_date : datetime
      
  end_date : datetime
      _description_
  spot_list : list
      _description_

  Returns
  -------
  list
      List of files between start_date and end_date.
  """
  b_prec = [] # lista dos arquivos de chuva na estação  
  b_vent = [] # lista dos arquivos de vento na estação 
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

def adaptingTXT(path, station_str) -> pd.DataFrame:                 # Util
  """Utilities for WRF output (forecast data). 
  Reading and formatting ".txt" data

  Parameters:
  -----------
      path (str): WRF output file

  Returns:
  --------
      pd.DataFrame: WRF output file formatted as pandas DataFrame
  """
  data = pd.read_csv(path, sep='\s+')
  pt_cols=['DATA', 'HORA',station_str,'Pto N','Pto S','Pto E','Pto W','Pto SE','Pto NE','Pto SW','Pto NW']
  vent_cols=['DATA',    'HORA',     station_str+'_ws10', station_str+'_wd10', 'Pto N_ws10',   'Pto N_wd10',   'Pto S_ws10',   'Pto S_wd10',   'Pto E_ws10',   'Pto E_wd10',   'Pto W_ws10',   'Pto W_wd10',   'Pto SE_ws10',  'Pto SE_wd10' , 'Pto NE_ws10' , 'Pto NE_wd10'  ,'Pto SW_ws10'  ,'Pto SW_wd10','Pto NW_ws10', 'Pto NW_wd10']

  try:
    data.drop(['Pto.8', 'SE_ws10', 'Pto.9', 'SE_wd10', 'Pto.10', 'NE_ws10', 'Pto.11',
       'NE_wd10', 'Pto.12', 'SW_ws10', 'Pto.13', 'SW_wd10', 'Pto.14',
       'NW_ws10', 'Pto.15', 'NW_wd10'], axis=1, inplace=True)
    data.columns=vent_cols
  except:
    data.drop(['Pto.4', 'SE', 'Pto.5', 'NE', 'Pto.6', 'SW', 'Pto.7','NW'], axis=1, inplace=True)
    data.columns=pt_cols
  
  return data

def files_selection(station, config_dict) -> str:                   # Util
  """
  1) Data will be unzipped from extrai_rna.zip to ./files/extrai_rna/ 
  2) Filtered for the specified station
  3) Filtered for the specified time range on config dict
  4) Files will be renamed to one specific format: Ex.: 'Barreto_YYYYMMDD.txt'
  5) Filtered files will be moved to the folder specified on config_dict. './files/config_dict_dir_name/'
  
  Parameters
  ----------
  station : str
      station for the case
  config_dict : dict
      dict provided provided from <setup.config_file_reading()>. Infos set on RNA_Setups.txt 

  Returns
  -------
  new_path : str 
      New WRF selected files directory path. Already filtered by date and station
  wrf_station_name : str
      Name of station on wrf formating
  """
  # To find files by name on WRF extraction folder. 
  
  dict_wrf_obsStation = {'Pé Pequeno':'Pequeno', 'Bonfim 2': 'Bonfim', 
       'Várzea das Moças':'VdasMocas', 'Tenente Jardim':'TJardim',
       'Engenho do Mato':'EngMato', 'Preventório':'Prevent', 
       'Igrejinha':'Igrejinha', 'Caramujo':'Caramujo',
       'Boa Vista':'BoaVista', 'Barreto 1':'Barreto', 
       'Piratininga':'Piratininga', 'Maria Paula':'MPaula',
       'Piratininga 2':'Piratin2', 'Itaipú':'Itaipu', 
       'Maravista':'Maravista', 'São Francisco 1':'SaoFranc',
       'Jurujuba':'Jurujuba', 'Morro do Palácio':'MdoPalacio',
        'Morro do Estado':'MdoEstado','Morro da Penha':'MdaPenha', 
        'Rio do Ouro':'RiodoOuro', 'Sapê':'Sape', 
        'Bairro de Fátima':'BFatima',
       'Morro do Castro':'MdoCastro', 'Travessa Beltrão':'TBeltrao',
        'Cavalão':'Cavalao', 'Santa Bárbara 2':'StaBarbara', 
        'Morro do Bumba':'MdoBumba', 
        'Maceió':'Maceio', 'Coronel Leôncio':'CLeoncio'} # Structure is: {'name_on_observed_data':'name_on_wrf_file'}

  print("\n--- Creating directory for extraction of the files.")
  #new_extraction_path = input('Enter the dir name for new extraction folder: ')
  new_extraction_path = config_dict['New_Dir']

  try:
    new_path = './files/' + new_extraction_path + '/'
    os.makedirs(new_path)
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


  # Filtering Station files. NEXT STEP!!
  files = os.listdir(temp_zip_path)
  barreto_list = []
  for cada in files:
    if dict_wrf_obsStation[station] in cada and 'Zone' not in cada: 
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
      #print('moving ' + temp_zip_path+file + 'to' + new_path)
      shutil.copy(temp_zip_path+ file, new_path)
  #except:
  #  print('\n--- The files have been filtered.')


  # treatment for each file on ./file/OctoberWRF
  for cada in os.listdir(new_path):
    path2 = new_path+cada
    #path2)
    csv = adaptingTXT(path2, dict_wrf_obsStation[station])
    #print('transforming ' + path2 +"to" + new_path + cada[:-3]+'.csv')
    csv.to_csv(new_path+cada[:-3]+'csv')
    os.remove(path2)

  if ".zip" in wrf_zip_path:
    shutil.rmtree(temp_zip_path)
    print('\n--- Removing the temporary extracted folder.')

  return new_path, dict_wrf_obsStation[station]

def concatening(lista, path) -> pd.DataFrame:                       # Util
  to_concat = []
  for cada in lista:
    to_concat.append(pd.read_csv(path+cada))

  return pd.concat(to_concat)

def wrf_formatting(wrf_data, initial_date, final_date):             # WRF
  """Adjusting to fit with the observed data.

  Parameters
  ----------
  wrf_data : pd.DataFrame
      
  initial_date : datetime
      
  final_date : datetime
      

  Returns
  -------
  pd.DataFrame
      WRF_data already selected between initial and final date from observed data.
  """
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

def bringing_observed_data(observed_path, st_date, ed_date):        # OBS
  """
  Brings in the observed data and filters date as setup conditions.

  Parameters
  ----------
  observed_path : _type_, optional
      _description_, by default obs_path
  st_date : datetime.date, 
      initial date, by default starting_date
  ed_date : datetime.date, 
      final date, by default ending_date

  Returns
  -------
  pd.DataFrame
      observed data filtered by date specified on RNA_Setups.txt
  """
  #obs = pd.read_csv(obs_path).drop('Unnamed: 0', axis=1)
  #obs = obs.rename(columns={'Hora Leitura': 'Data', '01 h':'precipitacao_observada'})
  obs = observed_data_reading(observed_path, station='Barreto 1', st_date=st_date, ed_date=ed_date) # NEXT STEP!!
  obs = obs.rename(columns={'data': 'Data', 'chuva 1h':'precipitacao_observada'})

  obs = obs.sort_values('Data')
  obs['Horario'] = obs['Data'].astype('datetime64[ns]').dt.time
  obs['Data'] = obs['Data'].astype('datetime64[ns]').dt.date

  obs['DATA-HORA'] = obs['Data'].astype(str) + ' ' + obs['Horario'].astype(str)
  obs['Datetime'] = obs['DATA-HORA'].apply(lambda x: datetime.datetime(int(x[:4]), int(x[5:7]), int(x[8:10]), int(x.split(' ')[1].split(':')[0])))
  obs = obs.drop('DATA-HORA', axis=1)
  obs = obs.sort_values('Datetime')

  filtering_by_date = obs.where((obs['Data']>=st_date) & (obs['Data']<=ed_date)).dropna()
  
  return filtering_by_date

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

  wrf_data = wrf_formatting(wrf_data, initial_date, final_date)

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
    missing_vento = wrf_formatting(missing_vento, initial_date=starting_date, final_date=ending_date)

    full_wrf = wrf_formatting(wrf_vars[variable][1], initial_date=starting_date, final_date=ending_date)

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



  new_path, wrf_station_name = files_selection(station=station, config_dict=config_dict)


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


  vento_full = concatening(b_vent, new_path)
  prec_full = concatening(b_prec, new_path)
  temp_full = concatening(b_temp, new_path)

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


  observed_filtered_by_date = bringing_observed_data(observed_path=obs_path, st_date=starting_date, ed_date=ending_date)

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
station = 'Igrejinha'

main(config_dict=config_dict, station=station)