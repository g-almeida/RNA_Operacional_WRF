# -*- coding: utf-8 -*-
'''
Treating observed data from the API (and from google drive files (optionally))
'''
import utilities as util
import pandas as pd
import datetime as dt
import numpy as np
import warnings
warnings.filterwarnings("ignore")

class ObservedData:
    """
    Class to read observed data from the API and define adaption methods for the neural network model.
    """

    def __init__(self, path, station=None, sheet_name=None, sep=',', st_date=None, ed_date=None):
        """
        Initializes ObservedData object already doing the UTC conversion.
        
        Optionally also treats the excel files earlier downloaded from lammoc's google drive.
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
        self.df : pd.DataFrame
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
        
        self.df = obs
        self.path = path
        self.sheet_name = sheet_name
        self.sep = sep
        self.station = station
        self.st_date = st_date
        self.ed_date = ed_date
        

    def API_treatment(self):
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
        obs_df = self.df
        station = self.station
        
        if station != None:
            obs_df = obs_df.where(obs_df['estação']==station).dropna()
        
        df_values = obs_df[['chuva 15m', 'chuva 1h', 'chuva 4h', 'chuva 24h', 'chuva 96h', 'chuva 30d']]
        for cada in df_values:
            obs_df[cada] = df_values[cada].apply(lambda x: util.float_converter(x))
        
        #after_filled = filling_nan_observed_data(obs_df=obs_df, st_date=self.st_date, ed_date=self.ed_date)  

        self.df = obs_df 
    
    def filling_nan_observed_data(self, filling_obs_database):
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

        primeira_data = self.st_date
        ultima_data = self.ed_date
        obs_df = self.df

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

        if len_missing_dates/len_total_dates > 0.2 and filling_obs_database==False:
            return print("More than 20% failures on observed data. | Aborting!")
        
        else:
            print('\n   --- (OBS) In a total of '+ str(len_total_dates) +' dates.' )
            print("   --- (OBS) We have found: "+ str(len_missing_dates) +" failures. \n             We'll be filling with observed data of the next days." )

            obs_df = obs_df.set_index('data',drop=False)
            new_df = pd.DataFrame(np.nan, index=missing_observed_dates, columns=obs_df.columns)
            new_df['data'] = new_df.index
            
            joined = pd.concat([obs_df, new_df]).sort_index()
            # Premissa: Se nao sei se está chovendo, vale a chuva da hr da frente. Preferi pra rede tentar antecipar
            filled_joined = joined.fillna(method='backfill')

            self.df = filled_joined

                  ###############################################################
                  ###################### Bringing Data  #########################
                      #     A) WRF output ------\
                      #                           } = Final Data.
                      #     B) OBSERVED Data ----/
                  ###############################################################
                  
def bringing_observed_data(observed_path, st_date, ed_date, station, filling_obs_database=False):        # OBS
  """
  Brings in the observed data to the main script <data_merge.py> already filtered by date as setup conditions
  Initializing the observed object (ObservedData)
  
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
  obs = ObservedData(observed_path, station=station, st_date=st_date, ed_date=ed_date) # NEXT STEP!!
  obs.API_treatment()
  obs.filling_nan_observed_data(filling_obs_database)
  obs = obs.df
  
  hourly_obs = obs.where(obs['data'].dt.minute==0).dropna()
  hourly_obs_acum01 = hourly_obs[['data', 'chuva 1h']]

  obs = hourly_obs_acum01.rename(columns={'data': 'Data', 'chuva 1h':'precipitacao_observada'})

  obs = obs.sort_values('Data')
  obs['Horario'] = obs['Data'].astype('datetime64[ns]').dt.time
  obs['Data'] = obs['Data'].astype('datetime64[ns]').dt.date

  obs['DATA-HORA'] = obs['Data'].astype(str) + ' ' + obs['Horario'].astype(str)
  obs['Datetime'] = obs['DATA-HORA'].apply(lambda x: dt.datetime(int(x[:4]), int(x[5:7]), int(x[8:10]), int(x.split(' ')[1].split(':')[0])))
  obs = obs.drop('DATA-HORA', axis=1)
  obs = obs.sort_values('Datetime')

  filtering_by_date = obs.where((obs['Data']>=st_date) & (obs['Data']<=ed_date)).dropna()
  
  return filtering_by_date

def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +dt.timedelta(hours=t.minute//30))

def checking_observed_data_availability(path:str) -> bool:
    obs_data = pd.read_csv(path)
    obs_data['data'] = pd.to_datetime(obs_data['data'], format="%d/%m/%Y %H:%M")
    last_2_dates = obs_data.iloc[-5:]['data']

    last_1h = dt.datetime.now() - dt.timedelta(hours=1)
    last_2h = dt.datetime.now() - dt.timedelta(hours=2)
    rounded_last_1h = hour_rounder(last_1h)
    rounded_last_2h = hour_rounder(last_2h)

    return rounded_last_1h in list(last_2_dates) and rounded_last_2h in list(last_2_dates)
