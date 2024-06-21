import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, types, text
from sqlalchemy.dialects.postgresql import JSON as postgres_json
#from sqlalchemy_utils import database_exists, create_database
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


import os
import requests
import datetime
import json

import dash
from dash import Dash, html, dcc, dash_table, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc 

from dotenv import load_dotenv

# load your .env file and read all variables you need for the db connection and for weather api

load_dotenv()
weather_api_key = os.getenv("WEATHER_API_KEY")
username = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PW")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
db_climate = os.getenv("DB_CLIMATE")


        #config = dotenv_values("token.env")

        #username = config['POSTGRES_USER']
        #password = config['POSTGRES_PW']
        #host = config['POSTGRES_HOST']
        #port = config['POSTGRES_PORT']
        #db_climate = config['DB_CLIMATE']

url = f'postgresql://{username}:{password}@{host}:{port}/{db_climate}'

# create the engine

engine = create_engine(url, echo=True)

with engine.begin() as conn:
    result = conn.execute(text("SELECT * FROM mart_conditions_week;"))
    data = result.all()

# create a dataframe from it

weather_df = pd.DataFrame(data)

weather_df['avg_temp_c']=weather_df['avg_temp_c'].astype('float')
weather_df['lat']=weather_df['lat'].astype('float')
weather_df['lon']=weather_df['lon'].astype('float')
weather_df['max_temp_c']=weather_df['max_temp_c'].astype('float')
weather_df['min_temp_c']=weather_df['min_temp_c'].astype('float')
weather_df['total_precip_mm']=weather_df['total_precip_mm'].astype('float')
weather_df['total_snow_cm']=weather_df['total_snow_cm'].astype('float')
weather_df['avg_humidity']=weather_df['avg_humidity'].astype('float')
weather_df['daily_chance_of_rain_avg']=weather_df['daily_chance_of_rain_avg'].astype('float')
weather_df['daily_chance_of_snow_avg']=weather_df['daily_chance_of_snow_avg'].astype('float')

df_iso_codes = pd.read_csv('iso_codes.csv', index_col=0)

df_all = weather_df.merge(df_iso_codes, how='left', on='country')

df_grouped_weather_bucket_time = weather_df.groupby(['year_and_week','weather_bucket'])['avg_temp_c'].mean().reset_index()


df_sing = df_all[df_all['country']=='Singapore']
df_sing = df_sing.groupby('year_and_week')[['avg_temp_c', 'total_precip_mm', 'avg_humidity']].mean().round(2).reset_index()

df_asia =df_all[df_all['region']=='Asia']
df_asia = df_asia.groupby(['year_and_week','city'])[['avg_temp_c', 'total_precip_mm', 'avg_humidity']].mean().round(2).reset_index()


# Interactive component
dropdown = dcc.Dropdown(options=['Singapore', 'Shanghai', 'Manila'], value='Singapore', clearable=False)

#Graph
fig = px.bar(df_asia, 
             x='year_and_week', 
             y='avg_temp_c',  
             color='city',
             barmode='group',
             height=300, title = "Singapore vs Shanghai vs Manila: avg temperatures",
             color_discrete_map = {'Singapore': '#7FD4C1', 'Shanghai': 'orange', 'Manila': '#F7C0BB'})

fig = fig.update_layout(
        plot_bgcolor="DarkBlue", paper_bgcolor="DarkBlue", font_color="white"
    )

graph = dcc.Graph(figure=fig)


#Graph 2
fig2 = px.line(df_asia, x='year_and_week', y='avg_temp_c', height=300, title="Avg temperature in Celsius", markers=True)
fig2 = fig2.update_layout(
        plot_bgcolor="#222222", paper_bgcolor="#222222", font_color="white"
    )
graph2 = dcc.Graph(figure=fig2)

#Graph3
fig3 = make_subplots(specs=[[{"secondary_y": True}]], subplot_titles=('Precipitation vs Humidity in Singapore','Plot 2'))

fig3.add_trace(
    go.Scatter(x=df_sing['year_and_week'], y=df_sing['avg_humidity'], name="Avg humidity", mode="lines"),
    secondary_y=True
)

fig3.add_trace(
    go.Bar(x=df_sing['year_and_week'], y=df_sing['total_precip_mm'], name="Precipitation"),
    secondary_y=False
)

fig3.update_xaxes(title_text="Year-week")

        # Set y-axes titles
fig3.update_yaxes(title_text="Precipitation", secondary_y=False)
fig3.update_yaxes(title_text="Avg humidity", secondary_y=True)

graph3 = dcc.Graph(figure=fig3)



#Graph4
fig4 = px.choropleth(df_all, locations='alpha-3',
                    projection='winkel tripel', #see different options above
                    scope='asia', ## or schope='europe' or 'asia'
                    color='avg_temp_c', locationmode='ISO-3',
                    animation_frame="year_and_week", #lat=[1.29,14.60], lon=[103.86,120.98],
                    hover_name="timezone_id", center={'lat': 1.29, 'lon': 103.86}, width=800,height=600)

graph4 = dcc.Graph(figure=fig4)

#Graph 5
fig5=px.scatter(df_all, 
           x="avg_temp_c", 
           y="max_temp_c", 
           animation_frame="year_and_week", 
           size="will_it_rain_days", 
           color="region", hover_name="country", 
           log_x=True, size_max=55)#, range_x=[100,100000], range_y=[25,90])

graph5 = dcc.Graph(figure=fig5)


#Graph 6
fig6 = px.bar(df_grouped_weather_bucket_time, 
             x='year_and_week', 
             y='avg_temp_c',  
             color='weather_bucket',
             barmode='group', # if barmode= is removed, it will be a stacked bar graph
             orientation='v',
             height=400, title ='Avg temperature per weather bucket and per week')

graph6 = dcc.Graph(figure=fig6)

#Main code

        #instanciate the app
app =dash.Dash(external_stylesheets=[dbc.themes.SKETCHY])

        #add the command below after defining the app
server = app.server

        #the general syntax for a table
d_table = dash_table.DataTable(df_sing.to_dict('records'),
                                  [{"name": i, "id": i} for i in df_sing.columns],
                               style_data={'color': 'DarkMagenta','backgroundColor': 'azure'},
                              style_header={
                                  'backgroundColor': 'Cyan',
                                  'color': 'black','fontWeight': 'bold'
    })

dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df_sing.columns],
        data=df_sing.to_dict('records'),
        fixed_columns={'headers': True, 'data': 2},
        fixed_rows={'headers': True, 'data': 0},
        style_table={
            'minHeight': '400px', 'height': '400px', 'maxHeight': '400px',
            'minWidth': '900px', 'width': '900px', 'maxWidth': '900px'
        },
    )

table_updated2 = dash_table.DataTable(df_sing.to_dict('records'),
                                  [{"name": i, "id": i} for i in df_sing.columns],
                               style_data={'color': 'DarkMagenta','backgroundColor': 'azure'},
                              style_header={'backgroundColor': 'Cyan','color': 'black','fontWeight': 'bold'},
                                     style_table={
                                         'minHeight': '400px', 'height': '400px', 'maxHeight': '400px',
                                         'minWidth': '900px', 'width': '900px', 'maxWidth': '900px', 
                                         'marginLeft': 'auto', 'marginRight': 'auto',
                                     'marginTop': 0, 'marginBottom': 0} 
                                     )

            # set app layout
app.layout = html.Div([html.H1('Temperature Analysis in Singapore', style={'textAlign': 'center', 'color': 'coral'}), 
                       html.H2("Using the weather data from WeatherAPI.com, we take a look at Singapore's profile", style ={'paddingLeft': '30px'}),
                       html.H3('These are the findings:'),
                       html.Div([html.Div('SINGAPORE', 
                                          style={'backgroundColor': 'coral', 'color': 'white', 
                                                 'textAlign': 'center', 'width': '900px',
                                                  'marginLeft': 'auto', 'marginRight': 'auto', 
                                                  'marginTop':25, 'marginBottom':25,'width':450}),
                                 table_updated2, graph3, dropdown, graph2, graph, graph6, graph4, graph5])
])

# Output(component_id='my-output', component_property='children'),
# Input(component_id='my-input', component_property='value')

# decorator - decorate functions

@callback(
    Output(graph2, "figure"),
    Input(dropdown, "value"))
def update_bar_chart(city): 
    mask = df_asia["city"] == city # coming from the function parameter
    fig2 =px.bar(df_asia[mask], x='year_and_week', y='avg_temp_c',  
             color='city',
             color_discrete_map = {'Singapore': '#7FD4C1', 'Shanghai': 'orange', 'Manila': '#F7C0BB'},
             barmode='group',
             height=400, title = "Singapore vs Shanghai & Manila: avg temperatures",)
    fig2 = fig2.update_layout(
        plot_bgcolor="#222222", paper_bgcolor="#222222", font_color="white"
    )

    return fig2 # whatever you are returning here is connected to the component property of the output

if __name__ == '__main__':
     app.run_server()