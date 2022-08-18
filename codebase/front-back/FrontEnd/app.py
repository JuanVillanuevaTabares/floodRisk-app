# -*- coding: utf-8 -*-
"""
Created on Thu May 12 19:43:28 2022

FrontEnd for Flooding Predictions App

@author: Edwin Cifuentes - Team30 DS4A - Cohort 6
Finish date: 7 de julio de 2022
"""
import time
import os
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import geopandas
import pandas as pd
import pytz
import dash
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_auth
import diskcache
from dash.long_callback import DiskcacheLongCallbackManager
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
from dash_extensions.javascript import arrow_function, assign
from dash_bootstrap_templates import load_figure_template
from datetime import date, timedelta, datetime


DATATIGERS_LOGO = 'img/data-tigers.png' #tambien  desde "https://data-tigers.com/data-tigers.jpeg"
yesterday = datetime.now(pytz.timezone("America/Bogota")) - timedelta(days=1)

VALID_USERNAME_PASSWORD_PAIRS = {
    'ds4a': 'otherPass',
    'token': 'token'
}

months = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}
##########################################################################
#                           datasets FROM HERE
##########################################################################
emergencies = pd.read_csv("./datasets/CONSOLIDADO_EMERGENCIAS 1998-2021 v26052022.csv", low_memory=False, dtype={'DIVIPOLA':str})
emergencies = emergencies.dropna(subset=["DIVIPOLA"])
emergencies.FECHA = pd.to_datetime(emergencies.FECHA, format="%d/%m/%Y")
emergencies["MUERTOS"]=emergencies["MUERTOS"].str.replace("[ |]", "", regex=True)
emergencies["MUERTOS"]=emergencies["MUERTOS"].str.replace(",", ".")
nans = emergencies.MUERTOS.isin(('', ' ', 'nan', np.nan))
emergencies.MUERTOS[nans] = 0
emergencies.MUERTOS = emergencies.MUERTOS.astype(float)
emergencies["HERIDOS"]=emergencies["HERIDOS"].str.replace("[ |]", "", regex=True)
emergencies["HERIDOS"]=emergencies["HERIDOS"].str.replace(",", ".")
nans = emergencies.HERIDOS.isin(('', ' ', 'nan', np.nan))
emergencies.HERIDOS[nans] = 0
emergencies.HERIDOS = emergencies.HERIDOS.astype(float)
emergencies["DESAPA."]=emergencies["DESAPA."].str.replace("[ |]", "", regex=True)
emergencies["DESAPA."]=emergencies["DESAPA."].str.replace(",", ".")
emergencies["DESAPA."]=emergencies["DESAPA."].replace({".": ""})
nans = emergencies["DESAPA."].isin(('', ' ', 'nan', np.nan))
emergencies["DESAPA."][nans] = 0
emergencies["DESAPA."] = emergencies["DESAPA."].astype(float)
emergencies["VIV.DESTRU."]=emergencies["VIV.DESTRU."].str.replace("[ |]", "", regex=True)
emergencies["VIV.DESTRU."]=emergencies["VIV.DESTRU."].str.replace(",", ".")
emergencies["VIV.DESTRU."]=emergencies["VIV.DESTRU."].replace({".": ""})
nans = emergencies["VIV.DESTRU."].isin(('', ' ', 'nan', np.nan))
emergencies["VIV.DESTRU."][nans] = 0
emergencies["VIV.DESTRU."] = emergencies["VIV.DESTRU."].astype(float)
emergencies["VIV.AVER."]=emergencies["VIV.AVER."].str.replace("[Q |]", "", regex=True)
emergencies["VIV.AVER."]=emergencies["VIV.AVER."].str.replace(",", ".")
emergencies["VIV.AVER."]=emergencies["VIV.AVER."].replace({".": ""})
nans = emergencies["VIV.AVER."].isin(('', ' ', 'nan', np.nan))
emergencies["VIV.AVER."][nans] = 0
emergencies["VIV.AVER."] = emergencies["VIV.AVER."].astype(float)
emergencies["FAMILIAS"]=emergencies["FAMILIAS"].str.replace(" ", "")
emergencies["FAMILIAS"]=emergencies["FAMILIAS"].str.replace(",", ".")
emergencies["FAMILIAS"]=emergencies["FAMILIAS"].replace({".": ""})
nans = emergencies["FAMILIAS"].isin(('', ' ', 'nan', np.nan))
emergencies["FAMILIAS"][nans] = 0
emergencies["FAMILIAS"] = emergencies["FAMILIAS"].astype(float)
risk_level = pd.read_csv("./datasets/risk_level.csv", dtype ={'Código Municipio':str}, encoding="utf-8")
risk_level.FECHA = pd.to_datetime(risk_level.FECHA, format="%Y-%m-%d")
divipola = pd.read_csv("./datasets/DIVIPOLA v04072022.csv", dtype ={'Código Departamento':str,'Código Municipio':str}, encoding="utf-8")
divipola = divipola.dropna(subset=["Código Municipio"])
municipios_geojson = geopandas.read_file('./datasets/MunicipiosVeredas19MB.json', driver='GeoJSON', encoding='utf-8')#load municipios' shape file
municipios_geojson = municipios_geojson.rename(columns={'DPTOMPIO':'Código Municipio'}) #renaming columns to match divipola df
departamentos = divipola[["Código Departamento","Nombre Departamento"]].groupby(["Código Departamento","Nombre Departamento"]).size().reset_index()
departamentos = departamentos[["Código Departamento","Nombre Departamento"]].sort_values(by="Nombre Departamento")
departamentos.reset_index(drop=True)
dict_departamentos = departamentos.set_index('Código Departamento').sort_values(by='Nombre Departamento').to_dict()['Nombre Departamento']
for _ in dict_departamentos:
    dict_departamentos[_] = str(_)+' - '+dict_departamentos[_]
municipios = divipola[["Código Departamento","Nombre Departamento","Código Municipio","Nombre Municipio"]].groupby(["Código Departamento","Nombre Departamento","Código Municipio","Nombre Municipio"]).size().reset_index()
municipios = municipios[["Código Departamento","Nombre Departamento","Código Municipio","Nombre Municipio"]].sort_values(by="Nombre Municipio")
municipios.reset_index(drop=True)
dict_municipios = municipios.set_index('Código Municipio').sort_values(by='Nombre Municipio').to_dict()['Nombre Municipio']
for _ in dict_municipios:
    dict_municipios[_] = str(_)+' - '+dict_municipios[_]

##########################################################################
#                      MAP PREPARATION FROM HERE
##########################################################################
classes = [0, 15, 30, 45, 60, 75, 90]
colorscale = ['#ADFF2F', '#FED976', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026'] #colorscale = ['#FFEDA0', '#FED976', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026']
style = dict(weight=.5, opacity=.5, color='white', dashArray='1', fillOpacity=0.7)
# Create colorbar.
ctg = ["{}+".format(cls, classes[i + 1]) for i, cls in enumerate(classes[:-1])] + ["{}+".format(classes[-1])]
colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=300, height=30, position="bottomleft")
# Geojson rendering logic, must be JavaScript as it is executed in clientside.
style_handle = assign("""function(feature, context){
    const {classes, colorscale, style, colorProp} = context.props.hideout;  // get props from hideout
    const value = feature.properties[colorProp];  // get value the determines the color
    for (let i = 0; i < classes.length; ++i) {
        if (value > classes[i]) {
            style.fillColor = colorscale[i];  // set the fill color according to the class
        }
    }
    return style;
}""")
# Create initial geojson .
df_risk_level_for_map = municipios_geojson.join(risk_level[risk_level.FECHA == risk_level.FECHA.max()].set_index('Código Municipio'), how = 'left', on='Código Municipio')
df_risk_level_for_map = df_risk_level_for_map.join(divipola.set_index('Código Municipio'), how = 'left', on='Código Municipio')
initial_geojson_path = './assets/geojson/Mapa_'+risk_level.FECHA.max().strftime("%Y-%m-%d")[0:10]+'.geojson'
if not os.path.exists(initial_geojson_path): 
    df_risk_level_for_map.to_file(initial_geojson_path, driver='GeoJSON')
df_risk_level_for_map.FECHA = df_risk_level_for_map.FECHA.dt.date
geojson = dl.GeoJSON(url=initial_geojson_path,  # url to geojson file
                     options=dict(style=style_handle),  # how to style each polygon
                     zoomToBounds=True,  # when true, zooms to bounds when data changes (e.g. on load)
                     zoomToBoundsOnClick=True,  # when true, zooms to bounds of feature (e.g. polygon) on click
                     hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray='')),  # style applied on hover
                     hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp="Risk Level"),
                     id="geojson")
# Create info control.
info_tool_tip = html.Div(children=[html.H5("Flooding predictions - Colombia",style={'color':'black'}),html.P("Hover over a municipio")], id="info_tool_tip", className="info",
                style={'color':'black',"position": "absolute", "top": "10px", "right": "10px", "z-index": "1000"})

##########################################################################
#                           APP DASH FROM HERE
##########################################################################
#Templete for Graphs
load_figure_template("cyborg")
#Diskcache
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

# Create app.
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    external_stylesheets=[dbc.themes.CYBORG],#SUPERHERO],
    prevent_initial_callbacks=True,
    long_callback_manager=long_callback_manager
)
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
app.title = "Team 30 - Early Risk Assessment of Communities Prone to Flooding"
app.config["suppress_callback_exceptions"] = True
server = app.server

##########################################################################
#                    NAVIGATION MENU APP FROM HERE
##########################################################################
# make a reuseable navitem for the different examples
nav_item1 = dbc.NavItem(dbc.NavLink("Predictions", href="/predictions", active="exact"))
nav_item2 = dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard", active="exact"))

# make a reuseable dropdown for the different examples
dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem(divider=True),
        dbc.DropdownMenuItem("Altitude", href="/altitude"),
        dbc.DropdownMenuItem("Precipitation", href="/precipitations"),
        dbc.DropdownMenuItem("Pressure", href="/pressure"),
        dbc.DropdownMenuItem("Temperature", href="/temperature"),
        dbc.DropdownMenuItem(divider=True),
    ],
    nav=True,
    in_navbar=True,
    label="Statistics",
)

# this example that adds a logo to the navbar brand
navigation_bar = dbc.Navbar(
    dbc.Container([
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row([
                    dbc.Col(html.Img(src = app.get_asset_url(DATATIGERS_LOGO), height="40px")),
                ],
                align="center",
                className="g-0",
            ),
            href="https://data-tigers.com",
            style={"textDecoration": "none"},
        ),
        dbc.Col(dbc.NavbarBrand("TEAM 30 - Flooding Analytics", className="ms-2")),
        dbc.NavbarToggler(id="navbar-toggler2", n_clicks=0),
        dbc.Collapse(
            dbc.Nav(
                [nav_item1, nav_item2],# dropdown],
                className="ms-auto",
                navbar=True,
                pills=True,
            ),
            id="navbar-collapse2",
            navbar=True,
        ),
        dbc.Col(
            dbc.Nav(
                dbc.Container(dbc.NavItem(dbc.NavLink("Sign out", href="https://www.data-tigers.com"))),
                navbar=True,
            ),
            width="auto",
        ),
    ],),
    color="#282828",
    dark=True,
)


##########################################################################
#                       APP GRAPHS FROM HERE
##########################################################################
flooding_by_year = emergencies[emergencies['EVENTO'].str.contains('INUN').fillna(False) & (emergencies['FECHA']>'1998-01-01')].groupby([emergencies.FECHA.dt.year]).size().to_frame('size').rename_axis(['year']).reset_index()
flooding_by_year = px.bar(flooding_by_year, x="year", y="size", title="Annual Flood Reports<br>Source: UNGRD Emergencies 1998-2021", labels={'year': 'Year', 'size':'Number of Floods'})
flooding_by_year.update_xaxes(tickformat='d', type='category',tickangle=-45)

flooding_by_month = emergencies[emergencies['EVENTO'].str.contains('INUN').fillna(False) & (emergencies['FECHA']>'1998-01-01')].groupby([emergencies.FECHA.dt.month]).size().to_frame('size').rename_axis(['month']).reset_index()
flooding_by_month= px.bar(flooding_by_month, x=["month"], y="size", title="Annual Flood Reports (Monthly aggregate analysis)<br>Source: UNGRD Emergencies 1998-2021)", labels={'year': 'Year', 'size':'Number of Floods'})
for idx in range(len(flooding_by_month.data)):
    flooding_by_month.data[idx].x = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
flooding_by_month.update_xaxes(tickangle=-45,title=None)
flooding_by_month.update_layout(showlegend=False)

flooding_by_calendar_day = emergencies[emergencies['EVENTO'].str.contains('INUN').fillna(False) & (emergencies['FECHA']>'1998-01-01')].groupby([emergencies.FECHA.dt.day]).size().to_frame('size').rename_axis(['day']).reset_index()
flooding_by_calendar_day= px.bar(flooding_by_calendar_day, x=["day"], y="size", title="Annual Flood Reports (Daily aggregate analysis)<br>Source: UNGRD Emergencies 1998-2021", labels={'value': 'Calendar Day', 'size':'Number of Floods'})
flooding_by_calendar_day.update_layout(showlegend=False)

flooding_by_week_day = emergencies[emergencies['EVENTO'].str.contains('INUN').fillna(False) & (emergencies['FECHA']>'1998-01-01')].groupby([emergencies.FECHA.dt.dayofweek]).size().to_frame('size').rename_axis(['day']).reset_index()
flooding_by_week_day= px.bar(flooding_by_week_day, x=["day"], y="size", title="Flood reports by day of de week (UNGRD 1998-2021)", labels={'value': 'Day', 'size':'Number of Floods'})
for idx in range(len(flooding_by_week_day.data)):
    flooding_by_week_day.data[idx].x = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
flooding_by_week_day.update_layout(showlegend=False)

highest_risk_levels = df_risk_level_for_map.sort_values(by="Risk Level",ascending=False).head(20)
highest_risk_levels = px.bar(highest_risk_levels, x="Nombre Municipio", y="Risk Level", title="Top 20 - Highest Risk Levels for Colombia on: "+risk_level.FECHA.max().strftime("%Y-%m-%d"))
highest_risk_levels.update_xaxes(tickangle=-45, title=None)
highest_risk_levels.update_layout(autosize=True)

kill_injuries_missings = emergencies[emergencies['EVENTO'].str.contains('INUN').fillna(False) & (emergencies['FECHA']>'1998-01-01')].groupby([emergencies.FECHA.dt.year]).agg(
    kills=('MUERTOS', sum),
    injuries=('HERIDOS', sum),
    missings=('DESAPA.', sum),).reset_index()
fig_kill_injuries_missings = go.Figure()
fig_kill_injuries_missings.add_trace(go.Scatter(y=kill_injuries_missings['kills'], x=kill_injuries_missings["FECHA"],
                    mode='lines+markers',
                    name='Kills'))
fig_kill_injuries_missings.add_trace(go.Scatter(y=kill_injuries_missings['injuries'], x=kill_injuries_missings["FECHA"],
                    mode='lines+markers',
                    name='Injuries'))
fig_kill_injuries_missings.add_trace(go.Scatter(y=kill_injuries_missings['missings'], x=kill_injuries_missings["FECHA"],
                    mode='lines+markers', 
                    name='Missings'))
fig_kill_injuries_missings.update_layout(title='Annual number of affected people due to flooding<br>Source: UNGRD Emergencies 1998-2021',
                   xaxis_title='Year',
                   yaxis_title='Number of people affected')

affected_housing = emergencies[emergencies['EVENTO'].str.contains('INUN').fillna(False) & (emergencies['FECHA']>'1998-01-01')].groupby([emergencies.FECHA.dt.year]).agg(
    destroyed=('VIV.DESTRU.', sum),
    damaged=('VIV.AVER.', sum),).reset_index()
fig_affected_housing = go.Figure()
fig_affected_housing.add_trace(go.Scatter(y=affected_housing['destroyed'], x=affected_housing["FECHA"],
                    mode='lines+markers',
                    name='Destroyed homes'))
# fig_affected_housing.add_trace(go.Scatter(y=affected_housing['damaged'], x=affected_housing["FECHA"],
#                     mode='lines+markers',
#                     name='Damaged homes'))
fig_affected_housing.update_layout(title='Annual number of affected housing due to flooding<br>Source: UNGRD Emergencies 1998-2021',
                   xaxis_title='Year',
                   yaxis_title='Number of damaged homes')

affected_families = emergencies[emergencies['EVENTO'].str.contains('INUN').fillna(False) & (emergencies['FECHA']>'1998-01-01')].groupby([emergencies.FECHA.dt.year,emergencies.FECHA.dt.month]).agg(
    mean_families=('FAMILIAS', 'mean')).rename_axis(['year','month']).reset_index()
affected_families.mean_families = affected_families.mean_families.round(0)
affected_families.month = affected_families.month.replace(months)
fig_affected_families = px.bar(affected_families, x="year", y="mean_families", color="month", 
                title="Annual AVG of families affected due to flooding<br>Source: UNGRD Emergencies 1998-2021", 
                labels={'mean_families': 'Average families per month','year':'Year'},
                color_discrete_sequence=px.colors.qualitative.Light24_r)
fig_affected_families.update_xaxes(tickformat='d', type='category',tickangle=-45)


##########################################################################
#                       APP LAYOUT FROM HERE
##########################################################################
app.layout = html.Div([
    dcc.Location(id="url"),
    navigation_bar,
    html.Div(id="app-content", 
        style={
            "margin-left": "1rem",
            "margin-right": "1rem",
            "padding": "1rem 1rem",
        }
    ),
    dcc.Store(id="input_cache"),    
    ]
)

##########################################################################
#         DIFERENT PAGES FROM HERE (PREDICTIONS, DASHBORAD ETC)
##########################################################################
predictions = html.Div([
                html.Div([
                    html.Br(),
                    html.Br(),
                    html.H4(children='Filters:',style = {'textAlign' : 'center','color':'white'}),
                    html.Br(),
                    dbc.Row([
                        dbc.Row(html.P("Select a date:",style={'color':'white'}),),
                        dbc.Row(
                            dcc.DatePickerSingle(
                                id='my-date-picker-single',
                                min_date_allowed=risk_level.FECHA.min(),
                                max_date_allowed=risk_level.FECHA.max(),
                                initial_visible_month=risk_level.FECHA.max(),
                                display_format='MMM Do, YY',
                                clearable=False,
                                date=risk_level.FECHA.max(),
                                style={ "z-index": "1000"}
                            ),
                        ),
                    ],
                    style={'text-align': 'center'}
                    ),
                    html.Br(),
                    html.Br(),
                    dcc.Dropdown(
                        options=dict_departamentos,
                        placeholder="Select a departamento",
                        id='list-departamento',
                    ),
                    html.Br(),
                    dcc.Dropdown(
                        placeholder="Select a municipio",
                        id='list-municipio',
                    ),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Div(
                        children=[
                            html.A(
                                href="https://data-tigers.com/",
                                target="_blank",
                                style={'text-decoration': 'none'},
                                children=["Powered by: ",html.Br(),"Team 30 DATA-TIGERS",html.Br(),],                                
                            ),
                            html.Div(children=["   ",
                                               html.Img(
                                                    src=app.get_asset_url(DATATIGERS_LOGO), 
                                                    #width="85", 
                                                    height="250",                                    
                                                ),
                                              ]),
                            
                        ],
                        style={
                            'justify-content': 'center',
                            'font-size': '14px',
                            'font-weight': '400',
                            'text-align': 'center',
                        }
                    ),                   
                ],
                className='col-lg-3 col-sm-12',
                style = { 'color':'black'}
                ),
                html.Div([
                    dl.Map(
                        center=[5.10971, -73.90175], 
                        zoom=5.75,
                        zoomDelta=0.25,  
                        zoomSnap=0.25,
                        children=[dl.TileLayer(url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png?api_key=f0ee2bb8-5687-4c1b-9ffc-92784e5726eb'), dl.GestureHandling(), geojson, colorbar, info_tool_tip],
                        # El anterior mapa es en tema oscuro para llevar al usuario hacia un objetivo el MAPA ------ El Mapa de color predeterminado aqui: children=[dl.TileLayer(), dl.GestureHandling(), geojson, colorbar, info_tool_tip],
                        id="graph-map"
                    ),
                    ],
                    className='col-lg-4 col-sm-12',
                    id="div-map",
                    style={'color':'white','padding' : '5px', 'height': '90vh', 'margin': "auto", "display": "block"}
                ),
                html.Div([
                    html.Div([
                        dash_table.DataTable(
                            id="table-risk-level",
                            data=df_risk_level_for_map[['Código Municipio','Nombre Municipio','Nombre Departamento', 'FECHA', 'Risk Level']].sort_values(by='Risk Level',ascending=False).to_dict('records'), 
                            columns=[
                                {"name": ["DIVIPOLA"], "id": 'Código Municipio', "hideable": "last"},
                                {"name": ["Municipio"], "id": 'Nombre Municipio', "hideable": "last"},
                                {"name": ["Departamento"], "id": 'Nombre Departamento', "hideable": "last"},
                                {"name": ["Risk Date"], "id": 'FECHA', "hideable": "last"},
                                {"name": ["Risk Level"], "id": 'Risk Level', "hideable": "last"},
                                ],
                            page_size=10,
                            filter_action="native",
                            sort_action="native",
                            export_format='xlsx',
                            export_headers='display',
                            style_header={
                                'backgroundColor': 'rgb(30, 30, 30)',
                                'color': 'white',
                                'border': '1px solid gray'
                            },
                            style_data={
                                'backgroundColor': 'rgb(50, 50, 50)',
                                'color': 'white',
                                'border': '1px solid gray',
                                'whiteSpace': 'normal',
                                'height': 'auto',
                                'lineHeight': '15px'
                            },
                        )
                        ],
                        style={'color':'black','height': '53vh'}
                    ),
                    html.Div([
                        html.Div([dcc.Graph(id='graph-risk-level',figure=highest_risk_levels,style={'height': '37vh'}),],),
                        ],
                    ),
                    ],
                    className='col-lg-5 col-sm-12',
                ),
                ],
                className='row',
            ),

dashboard = [html.Div([
                html.H2(children='Flooding Reports - Dashboard',
                        style = {'textAlign' : 'center'}
                )],
                className='col-12',
            ),
            html.Div([
                dcc.RangeSlider(
                    min=1998,
                    max=2021,
                    step=1,
                    marks={1998: {'label': '1998'},
                            2001: {'label': '2001'},
                            2004: {'label': '2004'},
                            2007: {'label': '2007'},
                            2010: {'label': '2010'},
                            2013: {'label': '2013'},
                            2016: {'label': '2016'},
                            2019: {'label': '2019'},
                            2021: {'label': '2021'}
                          },
                    value=[1998, 2021],
                    tooltip={"placement": "bottom", "always_visible": True}, 
                    allowCross=True, 
                    id="slider-anios"),
                ]
            ),
            html.Div([
                html.Div([dcc.Graph(id='affected-families',figure=fig_affected_families),],
                    className='col-lg-4 col-sm-12',
                    style = {'padding' : '5px'}
                ),                
                html.Div([dcc.Graph(id='affected-people',figure=fig_kill_injuries_missings),],
                    className='col-lg-4 col-sm-12',
                    style = {'padding' : '5px'}
                ),
                html.Div([dcc.Graph(id='affected-housing',figure=fig_affected_housing),],
                    className='col-lg-4 col-sm-12',
                    style = {'padding' : '5px'}
                ),
                ],
                className='row',
            ),
            html.Div([
                html.Div([dcc.Graph(id='flooding_by_year',figure=flooding_by_year),],
                    className='col-lg-4 col-sm-12',
                    style = {'padding' : '5px'}
                ),
                html.Div([dcc.Graph(id='flooding_by_month',figure=flooding_by_month),],
                    className='col-lg-4 col-sm-12',
                    style = {'padding' : '5px'}
                ),
                html.Div([dcc.Graph(id='flooding_by_calendar_day',figure=flooding_by_calendar_day),],
                    className='col-lg-4 col-sm-12',
                    style = {'padding' : '5px'}
                ),                
                ],
                className='row',
            ),]

statistics = html.Div([
        html.Div([],
            className='col-lg-1 col-sm-1',
            style = {'padding' : '5px'}
            ),
        html.Div([
                dl.Map(center=[4.60971, -74.08175], zoom=5, children=[
                        dl.TileLayer(),
                        dl.GestureHandling(),
                        dl.GeoJSON(url="./datasets/MunicipiosVeredas19MB.geojson",  # url to geojson file
                            id="municipios"),
                        ],
                        style={'width': '50%', 'height': '80vh', 'margin': "auto", "display": "block"}, 
                        id="map2"),    
            ],
            className='col-lg-10 col-sm-10',
            style = {'padding' : '5px'}
            ),
        html.Div([],
            className='col-lg-1 col-sm-1',
            style = {'padding' : '5px'}
            ),
        ],
        className='row',
    )
##########################################################################
#                           CALLBACKS FROM HERE
##########################################################################

# we use a callback to toggle the collapse on small screens
@app.callback(
    Output("navbar-collapse2", "is_open"),
    [Input("navbar-toggler2", "n_clicks")],
    [State("navbar-collapse2", "is_open")])
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# Callback for Map
@app.callback(
    Output("info_tool_tip", "children"),
    [Input("geojson", "hover_feature")])
def info_hover(feature):
    header = [html.H5("Flooding predictions - Colombia",style={'color':'black'})]
    if not feature:
        return header + [html.P("Hover over a municipio")]
    return header + [html.B(feature["properties"]["Nombre Municipio"]+'('+feature["properties"]["Nombre Departamento"]+')'), html.Br(),
                     "Risk Date: "+feature["properties"]["FECHA"][0:10],   html.Br(),
                     "Risk level: {:.2f}%".format(feature["properties"]["Risk Level"])]

#Callback for date, list departamento and list municipio
@app.callback(
    Output('list-municipio', 'options'),
    Output('table-risk-level', 'data'),
    Output('graph-risk-level', 'figure'),
    Output('geojson', 'url'),
    [Input("my-date-picker-single", "date"),
     Input("list-departamento", "value"),
     Input("list-municipio", "value"),],
    running=[
         (Output("my-date-picker-single", "disabled"), True, False),
         (Output("list-departamento", "disabled"), True, False),
         (Output("list-municipio", "disabled"), True, False),
    ],
    prevent_initial_call=True,
)
def update_map_table_graph(selected_date,selected_departamento,selected_municipio):
    dic_temp = {}
    if not selected_departamento == None:
        for key in dict_municipios:
            if key[0:2] == selected_departamento:
                dic_temp[key] = dict_municipios[key]
        
        df_risk_level_for_map = municipios_geojson[municipios_geojson['DPTO_CCDGO']==selected_departamento].join(risk_level[risk_level.FECHA == selected_date].set_index('Código Municipio'), how = 'left', on='Código Municipio')
        df_risk_level_for_map = df_risk_level_for_map.join(divipola.set_index('Código Municipio'), how = 'left', on='Código Municipio')
        path_geojson_file = './assets/geojson/Mapa_'+selected_date[0:10]+'_'+selected_departamento+'.geojson'
        if not os.path.exists(path_geojson_file): 
            df_risk_level_for_map.to_file(path_geojson_file, driver='GeoJSON')
        df_risk_level_for_map.FECHA = df_risk_level_for_map.FECHA.dt.date

        table_risk=df_risk_level_for_map[df_risk_level_for_map['Código Departamento']==selected_departamento][['Código Municipio','Nombre Municipio','Nombre Departamento', 'FECHA', 'Risk Level']].sort_values(by='Risk Level',ascending=False).to_dict('records')
        highest_risk_levels = df_risk_level_for_map[df_risk_level_for_map['Código Departamento']==selected_departamento].sort_values(by="Risk Level",ascending=False).head(20)
        highest_risk_levels = px.bar(highest_risk_levels, x="Nombre Municipio", y="Risk Level", title="Top 20 - Highest Risk Levels for Departmento: "+dict_departamentos[selected_departamento])
        highest_risk_levels.update_xaxes(tickangle=-45, title=None)
        highest_risk_levels.update_layout(autosize=True)
    else:
        df_risk_level_for_map = municipios_geojson.join(risk_level[risk_level.FECHA == selected_date].set_index('Código Municipio'), how = 'left', on='Código Municipio')
        df_risk_level_for_map = df_risk_level_for_map.join(divipola.set_index('Código Municipio'), how = 'left', on='Código Municipio')
        path_geojson_file = './assets/geojson/Mapa_'+selected_date[0:10]+'.geojson'
        if not os.path.exists(path_geojson_file): 
            df_risk_level_for_map.to_file(path_geojson_file, driver='GeoJSON')
        df_risk_level_for_map.FECHA = df_risk_level_for_map.FECHA.dt.date

        table_risk=df_risk_level_for_map[['Código Municipio','Nombre Municipio','Nombre Departamento', 'FECHA', 'Risk Level']].sort_values(by='Risk Level',ascending=False).to_dict('records')
        highest_risk_levels = df_risk_level_for_map.sort_values(by="Risk Level",ascending=False).head(20)
        highest_risk_levels = px.bar(highest_risk_levels, x="Nombre Municipio", y="Risk Level", title="Top 20 - Highest Risk Levels for Colombia")
        highest_risk_levels.update_xaxes(tickangle=-45, title=None)
        highest_risk_levels.update_layout(autosize=True)
    if not selected_municipio == None:
        highest_risk_levels = risk_level[risk_level['Código Municipio']==selected_municipio].copy()
        highest_risk_levels.FECHA = highest_risk_levels.FECHA.dt.date
        highest_risk_levels = px.line(highest_risk_levels, x='FECHA', y='Risk Level', title='Historic risk level for municipio: '+str(dict_municipios[selected_municipio]) , markers=True)
        highest_risk_levels.update_xaxes(type='category',tickangle=-45,title=None)
    


    return [{'label': dic_temp[i], 'value': i} for i in dic_temp],table_risk,highest_risk_levels,path_geojson_file

#Callback for rangeSlider (Dashboard)
@app.callback(
    Output('flooding_by_year', 'figure'),
    Output('flooding_by_month', 'figure'),
    Output('flooding_by_calendar_day', 'figure'),
    Output('affected-families', 'figure'),
    Output('affected-people', 'figure'),
    Output('affected-housing', 'figure'),
    [Input('slider-anios', 'value')])
def update_dashboard(value):
    flooding_by_year = emergencies[emergencies['EVENTO'].str.contains('INUN').fillna(False) & (emergencies['FECHA']>=str(value[0])+'-01-01') & (emergencies['FECHA']<=str(value[1])+'-12-31')].groupby([emergencies.FECHA.dt.year]).size().to_frame('size').rename_axis(['year']).reset_index()
    flooding_by_year= px.bar(flooding_by_year, x="year", y="size", title="Annual Flood Reports<br>Source: UNGRD Emergencies "+str(value[0])+"-"+str(value[1]), labels={'year': 'Year', 'size':'Number of Floods'})
    flooding_by_year.update_xaxes(tickformat='d', type='category')
    
    flooding_by_month = emergencies[emergencies['EVENTO'].str.contains('INUN').fillna(False) & (emergencies['FECHA']>=str(value[0])+'-01-01') & (emergencies['FECHA']<=str(value[1])+'-12-31')].groupby([emergencies.FECHA.dt.month]).size().to_frame('size').rename_axis(['month']).reset_index()
    flooding_by_month= px.bar(flooding_by_month, x=["month"], y="size", title="Annual Flood Reports (Monthly aggregate analysis)<br>Source: UNGRD Emergencies "+str(value[0])+"-"+str(value[1])+")", labels={'year': 'Year', 'size':'Number of Floods'})
    for idx in range(len(flooding_by_month.data)):
        flooding_by_month.data[idx].x = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    flooding_by_month.update_xaxes(tickangle=-45,title=None)
    flooding_by_month.update_layout(showlegend=False)

    flooding_by_calendar_day = emergencies[emergencies['EVENTO'].str.contains('INUN').fillna(False) & (emergencies['FECHA']>=str(value[0])+'-01-01') & (emergencies['FECHA']<=str(value[1])+'-12-31')].groupby([emergencies.FECHA.dt.day]).size().to_frame('size').rename_axis(['day']).reset_index()
    flooding_by_calendar_day= px.bar(flooding_by_calendar_day, x=["day"], y="size", title="Annual Flood Reports (Daily aggregate analysis)<br>Source: UNGRD Emergencies "+str(value[0])+"-"+str(value[1])+")", labels={'value': 'Calendar Day', 'size':'Number of Floods'})
    flooding_by_calendar_day.update_layout(showlegend=False)

    flooding_by_week_day = emergencies[emergencies['EVENTO'].str.contains('INUN').fillna(False) & (emergencies['FECHA']>=str(value[0])+'-01-01') & (emergencies['FECHA']<=str(value[1])+'-12-31')].groupby([emergencies.FECHA.dt.dayofweek]).size().to_frame('size').rename_axis(['day']).reset_index()
    flooding_by_week_day= px.bar(flooding_by_week_day, x=["day"], y="size", title="Flood reports by day of de week (UNGRD "+str(value[0])+"-"+str(value[1])+")", labels={'value': 'Day', 'size':'Number of Floods'})
    for idx in range(len(flooding_by_week_day.data)):
        flooding_by_week_day.data[idx].x = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    flooding_by_week_day.update_layout(showlegend=False)

    # Update for affected families graph 
    affected_families = emergencies[emergencies['EVENTO'].str.contains('INUN').fillna(False) & (emergencies['FECHA']>=str(value[0])+'-01-01') & (emergencies['FECHA']<=str(value[1])+'-12-31')].groupby([emergencies.FECHA.dt.year,emergencies.FECHA.dt.month]).agg(
        mean_families=('FAMILIAS', 'mean')).rename_axis(['year','month']).reset_index()
    affected_families.mean_families = affected_families.mean_families.round(0)
    affected_families.month = affected_families.month.replace(months)
    fig_affected_families = px.bar(affected_families, x="year", y="mean_families", color="month", 
                title="Annual AVG of families affected due to flooding<br>Source: UNGRD Emergencies "+str(value[0])+"-"+str(value[1]), 
                labels={'mean_families': 'Average families per month','year':'Year'},
                color_discrete_sequence=px.colors.qualitative.Light24_r)
    fig_affected_families.update_xaxes(tickformat='d', type='category',tickangle=-45)

    kill_injuries_missings = emergencies[emergencies['EVENTO'].str.contains('INUN').fillna(False) & (emergencies['FECHA']>=str(value[0])+'-01-01') & (emergencies['FECHA']<=str(value[1])+'-12-31')].groupby([emergencies.FECHA.dt.year]).agg(
        kills=('MUERTOS', sum),
        injuries=('HERIDOS', sum),
        missings=('DESAPA.', sum),).reset_index()
    fig_kill_injuries_missings = go.Figure()
    fig_kill_injuries_missings.add_trace(go.Scatter(y=kill_injuries_missings['kills'], x=kill_injuries_missings["FECHA"],
                        mode='lines+markers',
                        name='Kills'))
    fig_kill_injuries_missings.add_trace(go.Scatter(y=kill_injuries_missings['injuries'], x=kill_injuries_missings["FECHA"],
                        mode='lines+markers',
                        name='Injuries'))
    fig_kill_injuries_missings.add_trace(go.Scatter(y=kill_injuries_missings['missings'], x=kill_injuries_missings["FECHA"],
                        mode='lines+markers', 
                        name='Missings'))
    fig_kill_injuries_missings.update_layout(title='Annual number of affected people due to flooding<br>Source: UNGRD Emergencies '+str(value[0])+"-"+str(value[1]),
                    xaxis_title='Year',
                    yaxis_title='Number of people affected')

    affected_housing = emergencies[emergencies['EVENTO'].str.contains('INUN').fillna(False) & (emergencies['FECHA']>=str(value[0])+'-01-01') & (emergencies['FECHA']<=str(value[1])+'-12-31')].groupby([emergencies.FECHA.dt.year]).agg(
        destroyed=('VIV.DESTRU.', sum),
        damaged=('VIV.AVER.', sum),).reset_index()
    fig_affected_housing = go.Figure()
    fig_affected_housing.add_trace(go.Scatter(y=affected_housing['destroyed'], x=affected_housing["FECHA"],
                        mode='lines+markers',
                        name='Destroyed homes'))
    # fig_affected_housing.add_trace(go.Scatter(y=affected_housing['damaged'], x=affected_housing["FECHA"],
    #                     mode='lines+markers',
    #                     name='Damaged homes'))
    fig_affected_housing.update_layout(title='Annual number of affected housing due to flooding<br>Source: UNGRD Emergencies '+str(value[0])+"-"+str(value[1]),
                    xaxis_title='Year',
                    yaxis_title='Number of damaged homes')

    return flooding_by_year, flooding_by_month, flooding_by_calendar_day, fig_affected_families, fig_kill_injuries_missings, fig_affected_housing


#Callback for Navigationmenu
@app.callback(
    Output("app-content", "children"), 
    [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/" or pathname == "/predictions":
        return predictions
    elif pathname == "/dashboard":
        return dashboard
    elif pathname == "/altitude":
        return [html.H1("Altitude Statistics"),statistics]
    elif pathname == "/precipitations":
        return [html.H1("Precipitations Statistics"),statistics]
    elif pathname == "/pressure":
        return [html.H1("Pressure Statistics"),statistics]
    elif pathname == "/temperature":
        return [html.H1("Temperature Statistics"),statistics]   
    return dbc.Alert(
        [ # If the user tries to reach a different page, return a 404 message
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ], 
        color="dark"
    )

if __name__ == "__main__":
    # app.run_server(host='0.0.0.0', port=9000) # production
    app.run_server(host="0.0.0.0", port=8050, dev_tools_hot_reload=False)  # development

