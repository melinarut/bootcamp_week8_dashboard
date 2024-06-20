import dash
from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc 

# we of course need plotly and pandas
import plotly.express as px
import pandas as pd

df = px.data.gapminder()
df_germany = df[df['country']=='Germany']
df_germany = df_germany[['year', 'lifeExp', 'pop', 'gdpPercap']]
df_countries =df[df['country'].isin(['Germany', 'Belgium', 'Denmark'])]


#instanciate the app
app =dash.Dash(external_stylesheets=[dbc.themes.QUARTZ])

#add the command below after defining the app
server = app.server

#the general syntax for a table
d_table = dash_table.DataTable(df_germany.to_dict('records'),
                                  [{"name": i, "id": i} for i in df_germany.columns],
                                  style_data={'color': 'white','backgroundColor': 'teal'},
                              style_header={
                                  'backgroundColor': 'rgb(210, 210, 210)',
                                  'color': 'black','fontWeight': 'bold'}) 

# update the table size and align it in the center

table_updated = dash_table.DataTable(df_germany.to_dict('records'),
                                  [{"name": i, "id": i} for i in df_germany.columns],
                               style_data={'color': 'white','backgroundColor': 'black'},
                              style_header={
                                  'backgroundColor': 'rgb(210, 210, 210)',
                                  'color': 'black','fontWeight': 'bold'}, 
                                     style_table={
                                         'minHeight': '400px', 'height': '400px', 'maxHeight': '400px',
                                         'minWidth': '900px', 'width': '900px', 'maxWidth': '900px', 
                                         'marginLeft': 'auto', 'marginRight': 'auto',
                                     'marginTop': 0, 'marginBottom': 0} 
                                     )
#adding a figure
fig = px.bar(df_countries, 
             x='year', 
             y='lifeExp',  
             color='country',
             barmode='group',
             height=300, title = "Germany vs Denmark & Belgium",)

fig = fig.update_layout(
        plot_bgcolor="#222222", paper_bgcolor="#222222", font_color="white"
    )

graph = dcc.Graph(figure=fig)

fig2 = px.line(df_germany, x='year', y='lifeExp', height=300, title="Life Expectancy in Germany", markers=True)
fig2 = fig2.update_layout(
        plot_bgcolor="#222222", paper_bgcolor="#222222", font_color="white"
    )
graph2 = dcc.Graph(figure=fig2)

fig3 = px.choropleth(df_countries, locations='iso_alpha', 
                    projection='natural earth', animation_frame="year",
                    scope='europe',   #we are adding the scope as europe
                    color='lifeExp', locationmode='ISO-3', 
                    color_continuous_scale=px.colors.sequential.ice)

fig3 = fig3.update_layout(
        plot_bgcolor="#222222", paper_bgcolor="#222222", font_color="white", geo_bgcolor="#222222"
    )

# here we needed to change the geo color also to make the world black

graph3 = dcc.Graph(figure=fig3)
# set app layout
# app.layout = html.Div([html.H1('My First Spicy Dash', style={'textAlign': 'center', 'color': 'orange'}), 
#                        html.H2('Welcome', style ={'paddingLeft': '30px'}),
#                        html.H3('These are the Graphs'),
#                        html.Div([html.Div('Germany', style={'backgroundColor': 'coral', 'color': 'white'}),
#                                   table_updated,
#                                   graph]),
# ])


app.layout = html.Div([html.H1('Gap Minder Analysis of Germany', style={'textAlign': 'center', 'color': 'coral'}), 
                       html.H3("Using the gapminder data we take a look at Germany's profile"),
                       html.Div([html.Div('Germany', 
                                          style={'backgroundColor': 'coral', 'color': 'white', 
                                                 'width': '900px',
                                                  'marginLeft': 'auto', 'marginRight': 'auto'}),
                                                  table_updated,
                                html.Div(
                                    [dbc.Row(
                                    [dbc.Col(html.Div(graph)),
                                    dbc.Col(html.Div(graph2)),]),]), 
                                    graph3])

                    
])
if __name__ == '__main__':
     app.run_server()