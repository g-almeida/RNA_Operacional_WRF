import datetime
import pandas as pd

                  ###############################################################
                  ###################### Bringing Data  #########################
                      #     A) WRF outuput ------\
                      #                           } = Final Data.
                      #     B) OBSERVED Data ----/
                  ###############################################################
                  

def wrf_formatting(wrf_data, initial_date, final_date):             
  """
  Initializes WRF_varPrediction formatting data to later fit in with the observed data.

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


class WRF_DailyVar:
    """
    - Daily
    - 1 var
    - init = wrf_formatting()
    """

    def __init__(self, wrf_daily_data, initial_date, final_date):
        """
        Initializes WRF_varPrediction formatting data to later fit in with the observed data.

        Parameters
        ----------
        wrf_daily_data : pd.DataFrame
            
        initial_date : datetime
            
        final_date : datetime
            
        Returns
        -------
        pd.DataFrame
            WRF_data already selected between initial and final date from observed data.
        """
       
        self.daily_df = wrf_formatting(wrf_daily_data, initial_date, final_date)
        self.st_date = initial_date
        self.ed_date = final_date
        #self.var = 

    def missing_date_finder(self):
        """
        Função designada para verificar os dias faltantes no WRF a partir do arquivo de dados observados.
        Note que fará o recorte baseado na lista de datas do arquivo de dados observados. Então ele funcionará como uma espécie de máscara

        Returns:
        --------
            list: Lista das datas faltantes no WRF.
        """

        wrf_data = self.daily_df
        starting_date = self.st_date
        ending_date = self.ed_date

        full_datelist = list()
        while starting_date <= ending_date:
            starting_date += datetime.timedelta(days=1)
            full_datelist.append(starting_date)

        missing_dates = []
        for cada in full_datelist:
            if cada not in list(wrf_data['Data']) and cada not in missing_dates:
                missing_dates.append(cada)
        
        return missing_dates

class WRF_DailyFilled:
    """
    - Daily corrected
    - n vars (1-3); usually 'prec','temp' and 'vento'** but vento is not being used right now, would require updates.
    - init already fills the missing forecast with the day before.
    """

    def __init__(self, missing_dates_list, wrf_vars, starting_date, ending_date, wrf_station_name):
        """
        Inicializa WRF_DailyFilled preenchendo os dias faltantes na previsão com os dados da previsão anterior.

        Parameters:
        ----------
            missing_dates_list (list): forecast data
            wrf_vars (dictionary): dict of {Daily 48h WRF Forecast Data : Daily 24h WRF Forecast Data}

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
                
        
            missing_vento = WRF_DailyVar(missing_vento, initial_date=starting_date, final_date=ending_date).daily_df

            full_wrf = WRF_DailyVar(wrf_vars[variable][1], initial_date=starting_date, final_date=ending_date).daily_df

            variable_concat = pd.concat([missing_vento, full_wrf]).drop('Unnamed: 0', axis=1).dropna().sort_values('Datetime')

            # corrected_wrf is a dictionary with the missing values filled and each key is an atmospheric variable
            corrected_wrf.update({variable : variable_concat})
        
        # For unknown reason, pandas required to use pd.concat for datetime merging with observed data...
        # So, we manipulated to str
        for variable in corrected_wrf:
            if variable != 'vento': # not working with wind variable anymore, this would require an update!
                corrected_wrf[variable] = corrected_wrf[variable].astype(str).drop(['Data','Horario'],axis=1)
            
                # Setting column names:
                corrected_wrf[variable].rename(columns={
                    wrf_station_name:variable + '_prev_'+ wrf_station_name,
                    'Pto N':variable + '_prev_ptoN',
                    'Pto S':variable + '_prev_ptoS',
                    'Pto E':variable + '_prev_ptoE',
                    'Pto W':variable + '_prev_ptoW',
                    'Pto SE':variable + '_prev_ptoSE',
                    'Pto NE':variable + '_prev_ptoNE',
                    'Pto SW':variable + '_prev_ptoSW',
                    'Pto NW':variable + '_prev_ptoNW'}, inplace=True)
            
        # merging precipitation and temperature
        wrf_data = pd.merge(corrected_wrf['prec'], corrected_wrf['temp'], on='Datetime')
        
        self.daily_df = wrf_data
        self.st_date = starting_date
        self.ed_date = ending_date

            
