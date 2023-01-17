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
import utilities as util
import WRF.extraction as extract
import WRF.WRF_output_treatment as WRF_treat
import OBS.API_output_treatment as OBS_treat
import dashboard.dashboard as dashboard
#import pickle 

def removing_false_data(final_data):
  """
  This function removes outliers from the input data.

  Parameters:
  ----------
      final_data (pd.DataFrame)

  Returns:
  --------
      final_data (pd.DataFrame): DataFrame without outliers
  """
  print("\n--- Removing outliers ---")

  # Removing values under 0.
  str_type_columns = ['Data', 'Horario', 'Datetime']
  for col in final_data.columns:
      if col not in str_type_columns:
          # OBS.: Temperatures below 0 must be considered, so the following rule does not apply on temperature columns.
          if 'temp' not in col: 
            final_data[col] = final_data[col].apply(lambda x: float(x) if float(x) > 0 else 0)
            final_data[col] = final_data[col].apply(lambda x: 0 if float(x) > 500 else float(x))

  return final_data

def main(config_dict:dict, station:str, test_set=False):

                  ###############################################################
                  ###################### Bringing Data  #########################
                      #     A) WRF output ------\
                      #                           } = Final Data.
                      #     B) OBSERVED Data ----/
                  ###############################################################

  wrf_dict, wrf_station_name, starting_date, ending_date, new_path = extract.wrf_files_extraction(config_dict, station)
  
                  ###############################################################
                      ################## WRF - MISSING DATES ####################
                      # 1) Look for missing data on wrf data 
                      # 2) Replace with the day before forecast
                  ###############################################################

    # 1) Look for missing data on wrf 
  missing_dates = WRF_treat.WRF_DailyVar(wrf_dict['prec'][1], starting_date, ending_date).missing_date_finder() # this will be a list w/ the missing dates

  # The WRF_DailyFilled instance, consists in the final DataFrame (all variables concatenated)
  # with forecast data corrected based on the day before forecast.
  corrected_wrf = WRF_treat.WRF_DailyFilled(missing_dates, wrf_dict, starting_date, ending_date, wrf_station_name)
  wrf_data = corrected_wrf.daily_df

  # This section is only used when we're creating the test set for the neural network
  # The test set does not consider the observed data, so we end up the script before gets to it.
  if test_set==True: 
    # final considerations
    wrf_data = removing_false_data(wrf_data).set_index('Datetime')


    pre_input_name = config_dict['pre_input_filename'].split('.')[0] + '_' + station + '.csv'  
    wrf_data.to_csv("files/inputs/testSet/"+ pre_input_name)
    os.makedirs(new_path + "/testSet_input_files" )
    wrf_data.to_csv(new_path + "/testSet_input_files/" + pre_input_name)

    # Removing extracted_files folder
    shutil.rmtree(new_path)
    print("\n--- File created at: ./files/inputs/testSet/"+ pre_input_name)
    return print("\n--- This won't be seen on dashboard. For that, you'll need to set parameter testSet=False instead")
      
  
  #   ------------- B) Observed Data

  print("\n--- |OBS| ")
  # obs_path = 'UTC_series_Barreto_18-21.csv' - config file
  
  print('   --- (OBS) Entering observed data.')
  obs_path = config_dict['Obs_Path']

  observed_filtered_by_date = OBS_treat.bringing_observed_data(observed_path=obs_path, st_date=starting_date, ed_date=ending_date, station=station)

  # For unknown reason, pandas required to use pd.concat for datetime merging...
  # So, we manipulated to str
  observed_filtered_by_date = observed_filtered_by_date.drop(['Horario'],axis=1)
  observed_filtered_by_date['Datetime'] = observed_filtered_by_date['Datetime'].astype(str)
  
                  ###############################################################
                  ########### Finally putting WRF and Observed data together ####
                  ###############################################################

  # merging observed data
  final_data = pd.merge(observed_filtered_by_date, wrf_data, on='Datetime')
  # merging wind (no need to adjust colum names)
  #final_data = pd.merge(final_data, corrected_wrf['vent'], on='Datetime')
  

  # final considerantions
  final_data = removing_false_data(final_data)

                  ################################
                  ##### Exporting Final Data #####
                  ################################

  pre_input_name = config_dict['pre_input_filename'].split('.')[0] + '_' + station + '.csv'
  
  final_data.to_csv("files/inputs/pre-input/"+ pre_input_name)
  os.makedirs(new_path + "/input_files" )
  final_data.to_csv(new_path + "/input_files/" + pre_input_name)
  print("\n--- File created at: ./files/inputs/pre-input/"+ pre_input_name)

  # Removing extracted_files folder
  shutil.rmtree(new_path)

  print("\n--- All Done! ---")



print("""\n ____  _   _    _              _        _    __  __ __  __  ___   ____   _   _ _____ _____             
|  _ \| \ | |  / \            | |      / \  |  \/  |  \/  |/ _ \ / ___| | | | |  ___|  ___|             
| |_) |  \| | / _ \    _____  | |     / _ \ | |\/| | |\/| | | | | |     | | | | |_  | |_                
|  _ <| |\  |/ ___ \  |_____| | |___ / ___ \| |  | | |  | | |_| | |___  | |_| |  _| |  _|               
|_| \_\_| \_/_/   \_\         |_____/_/   \_\_|  |_|_|  |_|\___/ \____|  \___/|_|   |_|                                                                                                            """)

config_dict = setup.config_file_reading()

# Choose the desired station
station = 'Jurujuba'

main(config_dict=config_dict, station=station, test_set=False)

dashboard.launch_dashboard()