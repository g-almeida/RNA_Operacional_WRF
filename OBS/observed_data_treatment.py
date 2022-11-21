from OBS.API_output_treatment import observed_data_reading
import datetime

                  ###############################################################
                  ###################### Bringing Data  #########################
                      #     A) WRF outuput ------\
                      #                           } = Final Data.
                      #     B) OBSERVED Data ----/
                  ###############################################################
                  
def bringing_observed_data(observed_path, st_date, ed_date, station):        # OBS
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
  obs = observed_data_reading(observed_path, station=station, st_date=st_date, ed_date=ed_date) # NEXT STEP!!
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
