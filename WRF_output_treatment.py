"""
    Script designated to treat the output of the WRF model.
        The Functions in this section are able to select the interval of time. And also formats each of the desired files.
"""

import os
import shutil
import datetime
import pandas as pd
from zipfile import ZipFile


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

new_extraction_path = input('Enter the dir name for new extraction folder: ')

try:
  october_path = './files/' + new_extraction_path + '/'
  os.makedirs(october_path)
except:
  print('Jul_OctWRF folder already exists')
  exit()

try:
  # entering the wrf zip file: Ex: 'extrai_rn.zip'
  wrf_zip = input('Enter the name of the wrf compressed folder. \n (Usually "extrai_rn.zip")')
  origin_path = "./files/" + wrf_zip
  destination_path = "./files/"
  after_zip_path = destination_path + "extrai_rn/"
  os.makedirs(destination_path)
except:
  print('Folder extrai_rna already exists')



with ZipFile(origin_path, 'r') as zipObj:
  zipObj.extractall(destination_path)

print('Files unzipped')

files = os.listdir(after_zip_path)
print(files)
# Filtering Barreto files.
barreto_list = []
for cada in files:
  if 'Barreto' in cada and 'Zone' not in cada:
    barreto_list.append(cada)

# This is when the files are filtered by time

date = datetime.datetime(2021,7,10)
date2 = datetime.datetime(2021,10,20)
datefilter = files_date_filter(date, date2, barreto_list)

# Moving the filtered files to the folder ./files/OctoberWRF/
try:
  for file in files:
    if file in datefilter:
      # First path is the WRF provided data
      # Second path is the destination path for the filtered data (station and date)
      print('moving ' + after_zip_path+file + 'to' + october_path)
      shutil.move(after_zip_path+ file, october_path)
except:
  print('The files have already been filtered.')


# treatment for each file on ./file/OctoberWRF
for cada in os.listdir(october_path):
  
  path2 = october_path+cada
  print(path2)
  csv = adaptingTXT(path2)
  print('transforming ' + path2 +"to" + october_path + cada[:-3]+'.csv')
  csv.to_csv(october_path+cada[:-3]+'csv')
  os.remove(path2)

shutil.rmtree(after_zip_path)
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
obs_path = input('Enter the file name of the observed data: \n Usually "UTC_series_Barreto_18-21.csv" ')
obs = pd.read_csv('./files/' + obs_path).drop('Unnamed: 0', axis=1)
obs = obs.rename(columns={'Hora Leitura': 'Data', '01 h':'precipitacao_obsevada'})
obs = obs.sort_values('Data')
obs['Horario'] = obs['Data'].astype('datetime64[ns]').dt.time

obs['Data'] = obs['Data'].astype('datetime64[ns]').dt.date


obs['DATA-HORA'] = obs['Data'].astype(str) + ' ' + obs['Horario'].astype(str)
obs['Datetime'] = obs['DATA-HORA'].apply(lambda x: datetime.datetime(int(x[:4]), int(x[5:7]), int(x[8:10]), int(x.split(' ')[1].split(':')[0])))
obs = obs.drop('DATA-HORA', axis=1)
obs.sort_values('Datetime', inplace=True)


    # dates input - config file
      # example: initial date=2021-08-04, final_date=2021-10-20

st_date_input_ = input('Enter the initial date for observed data (yyyy-mm-dd): ')
st_date_split = st_date_input_.split('-')
starting_date = datetime.date(int(st_date_split[0]), int(st_date_split[1]), int(st_date_split[2]))


ed_date_input_ = input('Enter the final date for observed data (yyyy-mm-dd): ')
ed_date_split = ed_date_input_.split('-')
ending_date = datetime.date(int(ed_date_split[0]), int(ed_date_split[1]), int(st_date_split[2]))


New_Aug_Out = obs.where((obs['Data']>=starting_date) & (obs['Data']<=ending_date)).dropna()


    # looking for missing data on wrf data


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


missing_dates = missing_date_finder(vento_daily, New_Aug_Out) # this will be the missing dates
missing_dates_nb = {} # {yesterday : today}

for today in missing_dates:
  yesterday = today - datetime.timedelta(days=1)
  missing_dates_nb.update({float(yesterday.strftime('%Y%m%d')) : float(today.strftime('%Y%m%d'))})


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



#   ------------- Finally putting WRF and Observed data together
# *temporary* : deserves a better implementation 

New_Aug_Out['Barreto_ws10']=corrected_wrf['vento']['Barreto_ws10'].values
New_Aug_Out['Barreto_wd10']=corrected_wrf['vento']['Barreto_wd10'].values
New_Aug_Out['Pto N_ws10']=corrected_wrf['vento']['Pto N_ws10'].values
New_Aug_Out['Pto N_wd10']=corrected_wrf['vento']['Pto N_wd10'].values
New_Aug_Out['Pto S_ws10']=corrected_wrf['vento']['Pto S_ws10'].values
New_Aug_Out['Pto S_wd10']=corrected_wrf['vento']['Pto S_wd10'].values
New_Aug_Out['Pto E_ws10']=corrected_wrf['vento']['Pto E_ws10'].values
New_Aug_Out['Pto E_wd10']=corrected_wrf['vento']['Pto E_wd10'].values
New_Aug_Out['Pto W_ws10']=corrected_wrf['vento']['Pto W_ws10'].values
New_Aug_Out['Pto W_wd10']=corrected_wrf['vento']['Pto W_wd10'].values
New_Aug_Out['Pto SE_ws10']=corrected_wrf['vento']['Pto SE_ws10'].values
New_Aug_Out['Pto SE_wd10']=corrected_wrf['vento']['Pto SE_wd10'].values
New_Aug_Out['Pto NE_ws10']=corrected_wrf['vento']['Pto NE_ws10'].values
New_Aug_Out['Pto NE_wd10']=corrected_wrf['vento']['Pto NE_wd10'].values
New_Aug_Out['Pto SW_ws10']=corrected_wrf['vento']['Pto SW_ws10'].values
New_Aug_Out['Pto SW_wd10']=corrected_wrf['vento']['Pto SW_wd10'].values
New_Aug_Out['Pto NW_ws10']=corrected_wrf['vento']['Pto NW_ws10'].values
New_Aug_Out['Pto NW_wd10']=corrected_wrf['vento']['Pto NW_wd10'].values


New_Aug_Out['prec_prev_Barreto']=corrected_wrf['prec']['Barreto'].values
New_Aug_Out['prec_prev_ptoN']=corrected_wrf['prec']['Pto N'].values
New_Aug_Out['prec_prev_ptoS']=corrected_wrf['prec']['Pto S'].values
New_Aug_Out['prec_prev_ptoE']=corrected_wrf['prec']['Pto E'].values
New_Aug_Out['prec_prev_ptoW']=corrected_wrf['prec']['Pto W'].values
New_Aug_Out['prec_prev_ptoSE']=corrected_wrf['prec']['Pto SE'].values
New_Aug_Out['prec_prev_ptoNE']=corrected_wrf['prec']['Pto NE'].values
New_Aug_Out['prec_prev_ptoSW']=corrected_wrf['prec']['Pto SW'].values
New_Aug_Out['prec_prev_ptoNW']=corrected_wrf['prec']['Pto NW'].values

New_Aug_Out['temp_prev_Barreto']=corrected_wrf['temp']['Barreto'].values
New_Aug_Out['temp_prev_ptoN']=corrected_wrf['temp']['Pto N'].values
New_Aug_Out['temp_prev_ptoS']=corrected_wrf['temp']['Pto S'].values
New_Aug_Out['temp_prev_ptoE']=corrected_wrf['temp']['Pto E'].values
New_Aug_Out['temp_prev_ptoW']=corrected_wrf['temp']['Pto W'].values
New_Aug_Out['temp_prev_ptoSE']=corrected_wrf['temp']['Pto SE'].values
New_Aug_Out['temp_prev_ptoNE']=corrected_wrf['temp']['Pto NE'].values
New_Aug_Out['temp_prev_ptoSW']=corrected_wrf['temp']['Pto SW'].values
New_Aug_Out['temp_prev_ptoNW']=corrected_wrf['temp']['Pto NW'].values

# pre_input_name format example: 'UTC_AugOut_WRF_obs.csv''  - config file
pre_input_name = input("All done! \n\nPlease, enter the name of the file you want to save the data: \n (Format example: 'UTC_AugOut_WRF_obs.csv'")
New_Aug_Out.to_csv("./files/inputs/pre-input/"+ pre_input_name)
