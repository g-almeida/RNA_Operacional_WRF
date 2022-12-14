import pandas as pd
import datetime
import os
from zipfile import ZipFile
import shutil

                  ###############################################################
                  ###################### Files Selection   ######################
                      # Filters WRF data by:    
                      #     1) Station     |     2) Time_range
                  ###############################################################

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
    print('\n |ERROR|: Folder already exists. You may have to delete ./files/temp_extracted_files directory.')
    exit()

  # Entering WRF files
  print("\n--- |WRF| ")
  print("   --- (WRF) Entering WRF files.")
  # entering the wrf zip file: Ex: 'extrai_rn.zip'
  #wrf_zip = input('Enter the name of the wrf compressed folder. \n (Usually "extrai_rn.zip")')
  wrf_zip_path = config_dict['zip_file_path']

  # WRF files entries options:
  # 1 - Zip package
  # 2 - Existing Folder
  if ".zip" in wrf_zip_path:  # 1 - Zip package
    print("   --- (WRF) Unzipping the files.")

    destination_path = "./files/"
    temp_zip_path = destination_path + "extrai_rn/" # OBS.: this is necessary because the unzip creates a folder with its name
    #os.makedirs(destination_path)

    with ZipFile(wrf_zip_path, 'r') as zipObj:
      zipObj.extractall(destination_path)

    print('   --- (WRF) Files unzipped')

  else:  # 2 - Existing Folder
    temp_zip_path = wrf_zip_path + '/'
    print('   --- (WRF) Moving the files.')


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
    print('   --- (WRF) Removing the temporary extracted folder.')

  return new_path, dict_wrf_obsStation[station]

def concatening(lista, path) -> pd.DataFrame:                       # Util
  to_concat = []
  for cada in lista:
    to_concat.append(pd.read_csv(path+cada))

  return pd.concat(to_concat)
