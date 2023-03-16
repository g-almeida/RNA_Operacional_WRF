# -*- coding: utf-8 -*-
"""This script is meant to be hourly run on the lab server.
It will query the API and update the database with the new data.

For now, the database is a local csv file. Located inside the repository "./files/obs_data/hourly_data.csv"
"""
import sys
sys.path.append('../')
import datetime
import pandas as pd
import sys
sys.path.append("/home/lammoc/Gabriel/RNA_Operacional_WRF")
import API as api
import API_output_treatment
now = datetime.datetime.now()

# needs to be set for working properly on cron
path = '../../files/obs_data/historical_hourly_data.csv'
operational_path = '../../files/obs_data/operational_hourly_data.csv'

# commented due to application on CRON
#if str(now.minute) == '1':
def obs_query(path, operational:bool = False):

	new_data = api.api_niteroi('chuva')#.drop(' ', axis=1)
	try:
		old_data = pd.read_csv(path)        
		concat_data = pd.concat([old_data, new_data])
	except:
		print('No old data found, creating new one')
		concat_data = new_data    

	concat_data = concat_data[['Lat', 'lon', 'estação', 'cidade', 'data', 'chuva 15m', 'chuva 1h', 'chuva 4h', 'chuva 24h', 'chuva 96h', 'chuva 30d', 'atual ou atrasado','fonte do dado']]
	
	if operational == True:
		if len(concat_data) > 60:
			concat_data = concat_data[-60:]
	
	concat_data.to_csv(path)
		
obs_query(path)
obs_query(operational_path, operational=True)