# -*- coding: utf-8 -*-
#def config_file_reading(Config_Path='/home/github/RNA_Operacional_WRF'):
def config_file_reading(Config_Path='./'):
                
    ### Config variables
    Config_Path=Config_Path
    Config_file='RNA_Setups.txt'
    txt_config_file=open(Config_Path + '/' + Config_file)

    txt_config=list()

    New_Dir=0
    zip_file_path=0
    Obs_Path=0
    Dates={}
    pre_input_filename=0

    line=0
    for line in txt_config_file:        
        line=line.rstrip('\n')
        txt_config.append(line)        
        
    print('--- Reading inputs')
    line_count=0
    while line_count<len(txt_config):        
        if txt_config[line_count].startswith('#'):
            if 'Extraction_folder' in txt_config[line_count] and line_count<len(txt_config):
                line_count+=1
                while txt_config[line_count].startswith('#')==False:
                        if txt_config[line_count]!='':
                            New_Dir=str(txt_config[line_count].split(',')[1])
                        line_count+=1
                        if line_count>=len(txt_config): break

            if 'rna_zip_file' in txt_config[line_count] and line_count<len(txt_config):
                line_count+=1
                while txt_config[line_count].startswith('#')==False:
                        if txt_config[line_count]!='':
                            zip_file_path=str(txt_config[line_count].split(',')[1])
                        line_count+=1
                        if line_count>=len(txt_config): break

            if 'Observed_data_path' in txt_config[line_count] and line_count<len(txt_config):
                line_count+=1
                while txt_config[line_count].startswith('#')==False:
                        if txt_config[line_count]!='':
                            Obs_Path=str(txt_config[line_count].split(',')[1])
                        line_count+=1
                        if line_count>=len(txt_config): break

            if 'Dates' in txt_config[line_count] and line_count<len(txt_config):
                line_count+=1
                while txt_config[line_count].startswith('#')==False:
                        if txt_config[line_count]!='':
                            Dates.update({txt_config[line_count].split(',')[0]: str(txt_config[line_count].split(',')[1])})
                        line_count+=1
                        if line_count>=len(txt_config): break
                        
            if 'pre_input_filename' in txt_config[line_count] and line_count<len(txt_config):
                line_count+=1
                while txt_config[line_count].startswith('#')==False:
                        if txt_config[line_count]!='':
                            pre_input_filename=str(txt_config[line_count].split(',')[1])
                        line_count+=1
                        if line_count>=len(txt_config): break

    config_dictionary = {"New_Dir":New_Dir,
                        "zip_file_path":zip_file_path,
                        "Obs_Path":Obs_Path,
                        "Dates":Dates,
                        "pre_input_filename":pre_input_filename}
    return config_dictionary

#print(config_file_reading())
