from abc import ABC, abstractmethod
import pickle
import pandas as pd

test_folder_path = '../files/inputs/testSet'
test_file_list = ['UTC_JulOut_WRF_obs_Maceió.csv'] # later: os.listdir(test_folder_path) inside < model_execution() > function.

rna_folder_path = '../files/models'

class Import(ABC):
    def __init__(self, path, file):
        self.path = path
        self.file = file
        self.station = file.split('.')[0].split('_')[-1]

    @abstractmethod
    def file_read(self):
        pass

class ImportTestSet(Import):
    def file_read(self):
        return pd.read_csv(f'{self.path}/{self.file}')

class ImportRNA(Import):
    def file_read(self):
        print("veio até o pickle load")
        return pickle.load(open(f'{self.path}/{self.file}', 'rb'))


for test_file in test_file_list:
    importing_test_set = ImportTestSet(test_folder_path, test_file)
    test_set = importing_test_set.file_read()
    print(test_set)
    
    station = test_set.station
    importing_rna_model = ImportRNA(rna_folder_path, f'rna_{station}.sav')
    try: 
        rna_model = importing_rna_model.file_read()
        print(importing_rna_model.file_read())
    except:
        Exception("Isso não vai funcionar por enquanto msm. Preciso do pickle")
    
    # rna_model.fit(test_set)
