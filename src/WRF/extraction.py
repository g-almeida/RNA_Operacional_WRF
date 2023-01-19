import os
import sys
sys.path.append(os.getcwd()[:-4])
import utilities as util
import datetime

def wrf_files_extraction(config_dict:dict, station:str) -> dict:

                    ###############################################################
                    ###################### Files Selection   ######################
                        # Filters WRF data by:    
                        #     1) Station     |     2) Time_range
                    ###############################################################

    new_path, wrf_station_name = util.files_selection(station=station, config_dict=config_dict)

                    ###############################################################
                    ###################### Bringing Data  #########################
                        #     A) WRF output ------\
                        #                           } = Final Data.
                        #     B) OBSERVED Data ----/
                    ###############################################################

    # dates input - config file
        # example: initial date=2021-08-04, final_date=2021-10-20
    st_date_input_ = config_dict['Dates']['Initial_Date']
    st_date_split = st_date_input_.split('-')
    starting_date = datetime.date(int(st_date_split[0]), int(st_date_split[1]), int(st_date_split[2]))

    ed_date_input_ = config_dict['Dates']['Final_Date']
    ed_date_split = ed_date_input_.split('-')
    ending_date = datetime.date(int(ed_date_split[0]), int(ed_date_split[1]), int(st_date_split[2]))

    #   ------------- A) WRF output

    # barreto is the spot variable 
    # "new_path" is the inputed path for the files before stratification
    barreto = os.listdir(new_path)
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


    # vento_full = util.concatening(b_vent, new_path)
    prec_full = util.concatening(b_prec, new_path)
    temp_full = util.concatening(b_temp, new_path)

    # The daily WRF forecast file provides prediction to 2 days ahead. 
    # Primarly, we're only interested in the first one. 
    # Later, the second day will be used to fill missing forecasts. <filling_missing_forecast()>
    #vento_daily = vento_full.where(vento_full['HORA']<25).dropna()  
    prec_daily = prec_full.where(prec_full['HORA']<25).dropna()
    temp_daily = temp_full.where(temp_full['HORA']<25).dropna()

    #wrf_dict = {'vento': [vento_full, vento_daily], 'prec': [prec_full, prec_daily], 'temp': [temp_full, temp_daily]}
    wrf_dict = {'prec': [prec_full, prec_daily], 'temp': [temp_full, temp_daily]}

    return wrf_dict, wrf_station_name, starting_date, ending_date, new_path