# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import statsmodels as sm
import sys
sys.path.append('../')
import OBS.API_output_treatment as API_treat
import datetime

def launch_dashboard():
    print('\n--- Launching dashboard.')
    #   Setting up the App             -------------------------------   

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    colors = {
        'background': '#111111',
        'text': 'rgb(47,138,196)',
        'title': 'rgb(141,211,199)'
    }


    #   First section             -------------------------------             

    # "data_base" is the market prices provided dataset
    # This first section is adapting the dataset to plot on dashboard

    dict_wrf_obsStation = {'Pé Pequeno':'Pequeno', 'Bonfim 2': 'Bonfim', 
        'Várzea das Moças':'VdasMocas', 'Tenente Jardim':'TJardim',
        'Engenho do Mato':'EngMato', 'Preventório':'Prevent', 
        'Igrejinha':'Igrejinha', 'Caramujo':'Caramujo',
        'Boa Vista':'BoaVista', 'Barreto 1':'Barreto', 
        'Piratininga':'Piratininga', 'Maria Paula':'MPaula',
        'Piratininga 2':'Piratin2', 'Itaipú':'Itaipu', 
        'Maravista':'Maravista', 'São Francisco 1':'SaoFranc',
        'Jurujuba':'Jurujuba', 'Morro do Palácio':'MdoPalacio',
            'Morro do Estado':'MdoEstado','Morro da Penha':'MdaPenha', 
            'Rio do Ouro':'RiodoOuro', 'Sapê':'Sape', 
            'Bairro de Fátima':'BFatima',
        'Morro do Castro':'MdoCastro', 'Travessa Beltrão':'TBeltrao',
            'Cavalão':'Cavalao', 'Santa Bárbara 2':'StaBarbara', 
            'Morro do Bumba':'MdoBumba', 
            'Maceió':'Maceio', 'Coronel Leôncio':'CLeoncio'} # Structure is: {'name_on_observed_data':'name_on_wrf_file'}


    #path = ".././files/old_files/obs_data/hourly_data.csv"
    path = "/home/github/RNA_Operacional_WRF/files/inputs/pre-input"
    station_dict = {}
    for cada in os.listdir(path):
        file_name = cada.split('.')[0] # removing ".csv" from string
        estacao = file_name.split('_')[-1] # getting station name from string
        station_dict.update({estacao : cada}) # e.g.: {Travessa Beltrão : UTC_AugOut_WRF_obs_Travessa Beltrão.csv} 

    #   Second section             -------------------------------

    treated_data_dict = {}
    for cada in station_dict:
        treated_data_dict.update({str(cada) : pd.read_csv(path + '/' + station_dict[cada])})

    #{'label': 'Tenente Jardim', 'value': "treated_data_dict['Tenente Jardim']}
    dropdown_options = []
    for cada in station_dict:   
        dropdown_options.append({'label': str(cada), 'value': str(cada)})

    #treated_data_dict['Piratininga'].to_csv('WUPpiratining.csv')

    #   Third section             -------------------------------

    app.layout = html.Div(
            #style={'backgroundColor': colors['background']},
            children=[
            html.H1(children='RNA | WRF: Coleta de Dados Chuva observada - Niterói', style={
                'textAlign': 'center'}),#, 'color': colors['title']}),
            
            html.Div(children='''Nossa coleta de dados observados engloba as seguintes estações de Niterói:'''),
            
            dcc.Dropdown(
                id='demo-dropdown',
                options=dropdown_options,
                value='Barreto 1'
            ),
            html.Div(id='dd-output-container'),

            
            ])

    @app.callback(
        dash.dependencies.Output('dd-output-container', 'children'),
        dash.dependencies.Input('demo-dropdown', 'value'))

    def update_output(value):
        #changed_graph = [p['prop_id'] for p in dash.callback_context.triggered][0] 
        
        var = treated_data_dict[value]
        value_str = dict_wrf_obsStation[value]
        
        
        fig0 = px.line(var, x=var['Data'], y=var['precipitacao_observada'], title='Chuva observada na estação '+value) # observed plot
        fig0.add_scatter(x=var['Data'], y=var['prec_prev_'+value_str], name='WRF Forecast for '+value)#, title='Previsão de Chuva - WRF na estação '+value) # forecast plot
        #fig.update_layout(
        #    plot_bgcolor=colors['background'],
        #    paper_bgcolor=colors['background'],
        #    font_color=colors['text'])
        #px.line(var, x='Data', y='prec_prev_'+value)

        obs_graph = dcc.Graph(id='observed-graph', figure=fig0)
        #wrf_graph = dcc.Graph(id='forecast-graph', figure=fig1)
        return obs_graph#, wrf_graph

    #if __name__ == '__main__':
    #    print("checked for name == __main__")
    return app.run_server(debug=True)