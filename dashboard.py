# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import statsmodels as sm

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#   First section             -------------------------------             

# "data_base" is the market prices provided dataset
# This first section is adapting the dataset to plot on dashboard
data_base = pd.read_csv("./files/obs_data/hourly_data.csv")

# "fig0" is the variable with the plot itself
fig0 = px.scatter(data_base, title='Gráfico do fechamento de 2020 (R$) | (01/10 - 25/11)', trendline='ols')

#   Second section             -------------------------------

# Here we're accessing some data from "ONS", the same 'csv's can be downloaded at "http://www.ons.org.br/paginas/resultados-da-operacao/historico-da-operacao"
# It is necessary to adapt the datasets: 
df_ger = pd.read_csv("Simples_Geração_de_Energia_Dia_data.csv", sep=';')
df_dem = pd.read_csv("Simples_Demanda_Máxima_Semana_Dia_data.csv", sep=';')
df_car = pd.read_csv("Simples_Carga_de_Energia_Dia_Hora_data.csv", sep=';')
df_dem['time'] = pd.to_datetime(df_dem['Data Escala de Tempo 1 DM Simp 4'])
df_ger['time'] = pd.to_datetime(df_ger['Data Escala de Tempo 1 GE Simp 4'])
df_car['time'] = pd.to_datetime(df_car['Data Escala de Tempo 1 CE Simp 4'])
df_ger['value']=df_ger['Selecione Tipo de GE Simp 4']
df_dem['value']=df_dem['Selecione Tipo de DM Simp 4']
df_car['value']=df_car['Selecione Tipo de CE Simp 4']

df_ger = df_ger.drop(0)

def virgPont(data):
    ''' Replaces "," for "." . 
    '''
    subs = data.replace(',','.')
    return subs

def adapt(dataset):
    ''' Responsible for adapting the dataset and calculate monthly means along the 'time'
        Call signature ::
        -------

			adapt(dataset)
        
        Returns ::
        -------
        
            pd.DataFrame : pandas.DataFrame

        -------
    '''
    df = pd.DataFrame(data={'time': dataset['time'], 'values': dataset['value']})
    df['values'] = pd.to_numeric(df['values'].apply(virgPont))
    ds = df.set_index(df['time']).drop('time', axis=1).to_xarray().groupby("time.month").mean()
    df = ds.to_dataframe()
    return df

# Saving pandas.DataFrame's results to variables
df_ger = adapt(df_ger)
df_dem = adapt(df_dem)
df_car = adapt(df_car)


#   Third section             -------------------------------

app.layout = html.Div(children=[
    html.H1(children='Recomendation Dashboard for Hydro Norsk Brasil', style={
        'textAlign': 'center'}),

    html.Div(children='''
        Demanda, geração e carga média mensal (2016-2020)
    '''),
    dcc.Dropdown(
        id='demo-dropdown',
        options=[
            {'label': 'Demanda (2016-2020)', 'value': "df_dem"},
            {'label': 'Geração (2016-2020)', 'value': "df_ger"},
            {'label': 'Carga (2016-2020)', 'value': "df_car"}
        ],
        value='df_dem'
    ),
    html.Div(id='dd-output-container'),
    
    html.Button('Linear', id='btn-nclicks-1', n_clicks=0),

    html.Button('Trendline', id='btn-nclicks-2', n_clicks=0),

    html.Div(children="O preço do mercado tende a oscilar em função de diversas variáveis como clima (previsões climáticas), regulação, dentre outras. A metodologia abordou apenas a demanda, geração e carga dos últimos quatro anos, calculando a média mensal ao longo do ano. Em um primeiro momento, o intuitivo é olhar para a demanda. Seu comportamento mostra que os valores (MWh/h) ao final da curva são bem menores do que o os iniciais.  Após a virada do ano há um forte crescimento na demanda energética, provavelmente em função turismo ao longo do mês de janeiro que tende a movimentar bastante a economia no verão. Assim sendo, passamos a observar o lado da oferta pelos gráficos de geração e carga (MWmed). É perceptível como as curvas são parecidas, para que não haja grande variação do preço, a oferta tenta acompanhar a demanda apresentada. Com a alta demanda de Janeiro, os preços tenderão a subir e, então, o crescimento da oferta acompanhará na medida que for demandado. ", style={'textAlign':'center'}),

    html.Div(children='\nO gráfico a baixo apresenta o valor da energia em Reais (R$) nos últimos meses. O último valor apresentado é de 25 de novembro (logo após uma leve queda). Apesar do efeito pandemia que nos encontramos atualmente e o turismo assim como outras atividades que giram a economia não apresentarem a mesma produtividade, o gráfico do preço já mostra uma tendência de crescimento de outubro para cá, sendo então muito arriscado acreditar numa força tão fraca da demanda futura. Portanto, acredito que, em função da análise acima com os dados da ONS, o crescimento da demanda provocará em ainda maior elevação dos preços em janeiro antes que a geração a acompanhe. Dessa forma, recomendo a compra no atual valor de R$ 331.  ', style={'textAlign':'center'}),

    dcc.Graph(id='base-graph', figure=fig0)
    
])

@app.callback(
    dash.dependencies.Output('dd-output-container', 'children'),
    dash.dependencies.Input('demo-dropdown', 'value'),
    dash.dependencies.Input('btn-nclicks-1', 'n_clicks'),
    dash.dependencies.Input('btn-nclicks-2', 'n_clicks'))
def update_output(value, btn1, btn2):
    changed_graph = [p['prop_id'] for p in dash.callback_context.triggered][0]
    
    if value == "df_dem":
        var = df_dem
        if 'btn-nclicks-1' in changed_graph:
            fig = px.line(var, x=var.index, y='values', title='Média mensal da demanda ao longo do ano (MWh/h) | (2016-2020)')
            
        elif 'btn-nclicks-2' in changed_graph:
            fig = px.scatter(var, x=var.index, y='values', title='Média mensal da demanda ao longo do ano (MWh/h) | (2016-2020)', trendline='ols')
           
        else:
            fig = px.line(var, x=var.index, y='values', title='Média mensal da demanda ao longo do ano (MWh/h) | (2016-2020)')
            
        return dcc.Graph(id='example-graph', figure=fig)
    
    if value == "df_ger":
        var = df_ger
        if 'btn-nclicks-1' in changed_graph:
            fig = px.line(var, x=var.index, y='values', title='Média mensal da geração ao longo do ano (MWmed) | (2016-2020)')
            
        if 'btn-nclicks-2' in changed_graph:
            fig = px.scatter(var, x=var.index, y='values', title='Média mensal da geração ao longo do ano (MWmed) | (2016-2020)', trendline='ols')
            
        else:
            fig = px.line(var, x=var.index, y='values', title='Média mensal da geração ao longo do ano (MWmed) | (2016-2020)')
            
        return dcc.Graph(id='example-graph', figure=fig)
    
    if value == "df_car":
        var = df_car
        if 'btn-nclicks-1' in changed_graph:
            fig = px.line(var, x=var.index, y='values', title='Média mensal da carga ao longo do ano (MWmed) | (2016-2020)')
            fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
                font_color=colors['text'])
        if 'btn-nclicks-2' in changed_graph:
            fig = px.scatter(var, x=var.index, y='values', title='Média mensal da carga ao longo do ano (MWmed) | (2016-2020)', trendline='ols')
            fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
                font_color=colors['text'])
        else:
            fig = px.line(var, x=var.index, y='values', title='Média mensal da carga ao longo do ano (MWmed) | (2016-2020)')
            fig.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
                font_color=colors['text'])
        return dcc.Graph(id='example-graph', figure=fig)

if __name__ == '__main__':
    app.run_server(debug=True)