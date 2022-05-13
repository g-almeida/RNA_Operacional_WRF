# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import statsmodels as sm
import sys
sys.path.append('/home/github/RNA_Operacional_WRF')
import API_output_treatment as api_t

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
path = "./files/obs_data/hourly_data.csv"
station_list = pd.read_csv(path)['estação'].unique()



#   Second section             -------------------------------

treated_data_dict = {}
for cada in station_list:
    treated_data_dict.update({str(cada) : api_t.observed_data_reading(path, cada)})

#{'label': 'Tenente Jardim', 'value': "treated_data_dict['Tenente Jardim']}
dropdown_options = []
for cada in station_list:   
    dropdown_options.append({'label': str(cada), 'value': str(cada)})



#   Third section             -------------------------------

app.layout = html.Div(
        style={'backgroundColor': colors['background']},
        children=[
        html.H1(children='RNA | WRF: Coleta de Dados Chuva observada - Niterói', style={
            'textAlign': 'center', 'color': colors['title']}),
        
        html.Div(children='''Nossa coleta de dados observados engloba as seguintes estações de Niterói:''', style={'color': colors['title']}),
        
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

    fig = px.line(var, x=var.index, y='chuva 1h', title='Chuva observada na estação '+value)
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'])

    return dcc.Graph(id='example-graph', figure=fig)

if __name__ == '__main__':
    app.run_server(debug=True)