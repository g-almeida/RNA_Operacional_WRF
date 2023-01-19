import setup_reading_function as setup
from data_merge import main

print("""\n ____  _   _    _              _        _    __  __ __  __  ___   ____   _   _ _____ _____             
|  _ \| \ | |  / \            | |      / \  |  \/  |  \/  |/ _ \ / ___| | | | |  ___|  ___|             
| |_) |  \| | / _ \    _____  | |     / _ \ | |\/| | |\/| | | | | |     | | | | |_  | |_                
|  _ <| |\  |/ ___ \  |_____| | |___ / ___ \| |  | | |  | | |_| | |___  | |_| |  _| |  _|               
|_| \_\_| \_/_/   \_\         |_____/_/   \_\_|  |_|_|  |_|\___/ \____|  \___/|_|   |_|                                                                                                            """)

config_dict = setup.config_file_reading()

# Choose the desired station
station_list = ['Jurujuba']
for station in station_list:
    data = main(config_dict=config_dict, station=station, test_set=False)
