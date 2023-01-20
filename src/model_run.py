import setup_reading_function as setup
from data_merge import main
from RNA.preprocessing.preprocessing import Preprocessing
from abc import ABC, abstractmethod
import pickle
import pandas as pd

class Import(ABC):
    def __init__(self, path, file):
        self.path = path
        self.file = file
        self.station = file.split('.')[0].split('_')[-1]

    @abstractmethod
    def file_read(self):
        pass

class ImportTestSet(Import): # Not used, since this script runs the generation of the TestSet 
    def file_read(self):
        return pd.read_csv(f'{self.path}/{self.file}')

class ImportRNA(Import):
    def file_read(self):
        print("veio até o pickle load")
        return pickle.load(open(f'{self.path}/{self.file}', 'rb'))


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
    
    string = ' PREPROCESSING DATA '
    print(f'\n{string:-^120}\n')

    # Creating and Instantiating ``Preprocessing`` object
    print('-- Creating a Preprocessing object...')
    preprocessing = Preprocessing(dataframe=data, station=station)
    print('-- Done! Objected created!\n')

    # Drop wind-related features
    print('-- Dropping the wind-related features from dataframe...')
    preprocessing.drop_wind_features()
    print('-- Done! WRF wind-related outputs dropped!\n')

    # Rename the columns that contain the pluviometric station name
    print('-- Renaming columns...')
    preprocessing.rename_columns_with_station_name()
    print('-- Done! Set standardized column names!\n')

    # Replace negatives values by ZERO
    print('-- Replacing negative values by ZERO...')
    preprocessing.replace_negative_values(by=0)
    print('-- Done! Negative values sucessfully replaced!\n')

    print('-- Applying time shift on dataframe...')
    # # Include the past 2 hours observed precipitation means
    # try:
    #     preprocessing.backward_shift(shift=2)
    # except Exception as e:
    #     print("\n\n-- |ERROR| Observed data not available yet.")
    #     raise e
    # Include the WRF precipitation forecasts for the next 4 hours
    preprocessing.forward_shift(shift=4)
    print(
        '-- Done! '\
        'Included the past 2 hours observed precipitation means '\
        'and the WRF precipitation forecasts for the next 4 hours\n'
    )

    testSet = preprocessing.dataframe

    print(f'\n--- Executing Neural network model for: {station}')

    rna = ImportRNA(path='../files/models', file=f'rna_{station}.sav').file_read()

    rna.predict(testSet)

    
