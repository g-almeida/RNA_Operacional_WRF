import datetime

                  ###############################################################
                  ###################### Bringing Data  #########################
                      #     A) WRF outuput ------\
                      #                           } = Final Data.
                      #     B) OBSERVED Data ----/
                  ###############################################################
                  
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
