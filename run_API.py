"""This script is meant to be hourly run on the lab server.
"""

import datetime
import API as obs
import pandas as pd

now = datetime.datetime.now()

if str(now.minute) == '0':
    
    new_data = obs.api_niteroi('chuva')#.drop(' ', axis=1)
    try:
        old_data = pd.read_csv('./files/obs_data/hourly_data.csv')        
        concat_data = pd.concat([old_data, new_data])
    except:
        print('No old data found, creating new one')
        concat_data = new_data    

    concat_data = concat_data[['Lat', 'lon', 'estação', 'cidade', 'data', 'chuva 15m', 'chuva 1h',
       'chuva 4h', 'chuva 24h', 'chuva 96h', 'chuva 30d', 'atual ou atrasado',
       'fonte do dado']]
    concat_data.to_csv('./files/obs_data/hourly_data.csv')

    print(now)
