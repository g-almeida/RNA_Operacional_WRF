# RNA_Operacional_WRF
Aplicação de rede neural artificial multilayer perceptron para otimização do resultado da previsão do WRF operacional.

### Pipeline de Pré-Processamento 

- Para gerar o arquivo de pré-processamento, basta executar esses 2 passos:
    1) Defina o RNA_Setups.txt com o caminho do dado observado e previsão do WRF.
    2) Execute: <python data_merge.py> escolhendo uma estação dentro do script, isso trará todos os dados necessários de acordo com as datas no setup, teremos como saída um ".csv" com chuva observada e dado de previsão do WRF.
   

## -> Sobre cada lado do dado de entrada:
  - Precipitação Observada:
      - Script de download: <API.py>
          - Responsável por baixar os dados observados do banco de dados da prefeitura (ou INMET).
      - Script de tratamento: <API_output_treatment.py>
          - Trata os dados observados provenientes da API (ou fornecidos previamente pela prefeitura)

  - WRF_output_treatment.py:
        inputs: 
            - Diretório de arquivos do WRF (podem estar comprimidos como ".zip")
    


# RNA_Operacional_WRF 
Application of a Multilayer Perceptron Neural Network to optimize result of WRF forecast.

- To generate the RNA pre-input file, simply execute these 2 steps:
    1) Set RNA_Setups.txt with the path of observed precipitation and WRF forecast data
    2) run: <python data_merge.py> specifing one station inside the script, this will bring all necessary data according to dates on setup, we'll have an ".csv" output with observed precipitation data and WRF forecast together.
        
## -> About each input data:
  - Observed Precipitation:
      - Download script: <API.py>
          - Responsible for downloading the hourly observed data from the city hall database.
      - Secondary script: <API_output_treatment.py>
          - Treats observed data provided from the API (or previously provided from the city hall)
  - WRF_output_treatment.py:
    inputs: 
        - WRF files directory (can be compressed as ".zip")
  
          