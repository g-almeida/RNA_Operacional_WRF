'''
Treating observed data

!!! On first moment using the files provided from google drive
'''

import pandas as pd

def leitura_dados_observados(path, sheet_name=None):
    """
    Leitura dos dados obsevados
    Aceita .xlsx e .csv

    Parameters
    ----------
    path : str, path type
        
    sheet_name : str, optional
        Mês; Ex.: "Outubro" 

    Returns
    -------
    hourly_obs_acum01 : pandas.DataFrame
        Acumulado de hora em hora observados as 00:00

    """
    if path[-4:] == 'xlsx':
        obs = pd.read_excel(path, sheet_name)
    else:
        obs = pd.read_csv(path)
    obs['Hora Leitura'] = pd.to_datetime('Hora Leitura')
    hourly_obs = obs.where(obs['Hora Leitura'].dt.minute==0).dropna()
    hourly_obs_acum01 = hourly_obs[['Hora Leitura', '01 h']]
    
    return hourly_obs_acum01



#   ------ Concatening provided past data downloaded from Google Drive

novembro18_maio21 = leitura_dados_observados('./files/series_Barreto 1_18-21.csv')
junho21 = leitura_dados_observados('./files/series_Barreto 1_21.xlsx', 'Junho')
julho21 = leitura_dados_observados('./files/series_Barreto 1_21.xlsx', 'Julho')
agosto21 = leitura_dados_observados('./files/series_Barreto 1_21.xlsx', 'Agosto')
setembro21 = leitura_dados_observados('./files/series_Barreto 1_21.xlsx', 'Setembro')
outubro21 = leitura_dados_observados('./files/series_Barreto 1_21.xlsx', 'Outubro')
novembro21 = leitura_dados_observados('./files/series_Barreto 1_21.xlsx', 'Novembro')
dezembro21 = leitura_dados_observados('./files/series_Barreto 1_21.xlsx', 'Dezembro')

concat_list = [novembro18_maio21, junho21, julho21, agosto21, setembro21, outubro21, novembro21, dezembro21]

full = pd.concat(concat_list)
full.to_csv('./files/full_series_Barreto_18-21.csv')