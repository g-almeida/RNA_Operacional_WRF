import setup_reading_function as setup
from data_merge import main
from RNA.preprocessing.preprocessing import Preprocessing

print("""\n ____  _   _    _              _        _    __  __ __  __  ___   ____   _   _ _____ _____             
|  _ \| \ | |  / \            | |      / \  |  \/  |  \/  |/ _ \ / ___| | | | |  ___|  ___|             
| |_) |  \| | / _ \    _____  | |     / _ \ | |\/| | |\/| | | | | |     | | | | |_  | |_                
|  _ <| |\  |/ ___ \  |_____| | |___ / ___ \| |  | | |  | | |_| | |___  | |_| |  _| |  _|               
|_| \_\_| \_/_/   \_\         |_____/_/   \_\_|  |_|_|  |_|\___/ \____|  \___/|_|   |_|                                                                                                            """)

config_dict = setup.config_file_reading()

# Choose the desired station
station_list = ['Jurujuba']
for station in station_list:
    data = main(config_dict=config_dict, station=station, test_set=True)
    
    data.to_csv(r"C:\Users\a711301\LocalGab\local_environment\github\RNA_Operacional_WRF\src\gab\data.csv")
    
    string = ' PREPROCESSING DATA '
    print(f'\n{string:-^120}\n')

    # Creating and Instantiating ``Preprocessing`` object
    print('-- Creating a Preprocessing object...')
    preprocessing = Preprocessing(dataframe=data)
    print('-- Done! Objected created!\n')

    preprocessing.dataframe.to_csv(r"C:\Users\a711301\LocalGab\local_environment\github\RNA_Operacional_WRF\src\gab\obj.csv")

    # Drop wind-related features
    print('-- Dropping the wind-related features from dataframe...')
    preprocessing.drop_wind_features()
    print('-- Done! WRF wind-related outputs dropped!\n')

    preprocessing.dataframe.to_csv(r"C:\Users\a711301\LocalGab\local_environment\github\RNA_Operacional_WRF\src\gab\dropwind.csv")

    # Rename the columns that contain the pluviometric station name
    print('-- Renaming columns...')
    preprocessing.rename_columns_with_station_name()
    print('-- Done! Set standardized column names!\n')

    preprocessing.dataframe.to_csv(r"C:\Users\a711301\LocalGab\local_environment\github\RNA_Operacional_WRF\src\gab\rename.csv")

    # Replace negatives values by ZERO
    print('-- Replacing negative values by ZERO...')
    preprocessing.replace_negative_values(by=0)
    print('-- Done! Negative values sucessfully replaced!\n')

    preprocessing.dataframe.to_csv(r"C:\Users\a711301\LocalGab\local_environment\github\RNA_Operacional_WRF\src\gab\negative.csv")

    print('-- Applying time shift on dataframe...')
    # Include the past 2 hours observed precipitation means
    preprocessing.backward_shift(shift=2)
    # Include the WRF precipitation forecasts for the next 4 hours
    preprocessing.forward_shift(shift=4)
    print(
        '-- Done! '\
        'Included the past 2 hours observed precipitation means '\
        'and the WRF precipitation forecasts for the next 4 hours\n'
    )

    print(preprocessing.dataframe)