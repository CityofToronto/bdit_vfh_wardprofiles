import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import pandas.io.sql as pandasql
import plotly.graph_objs as go
from psycopg2 import connect

# for serving static images
# https://github.com/plotly/dash/issues/71
import base64

# bootstrap
import dash_bootstrap_components as dbc

###################################################################################################
#                                                                                                 #
#                                       Data Fetching                                             #
#                                                                                                 #
###################################################################################################

database_url = os.getenv("DATABASE_URL")
if database_url is not None:
    con = connect(database_url)
else:
    import configparser
    CONFIG = configparser.ConfigParser()
    CONFIG.read('config.cfg')
    dbset = CONFIG['DBSETTINGS']
    con = connect(**dbset)

# ** ward-stats **
df_rank = pandasql.read_sql('''
                         SELECT * FROM cnangini.wp_avg_daily_trips
                         ''', con)

df_vkt = pandasql.read_sql('''
                         SELECT * FROM cnangini.wp_vkt
                         ''', con)

df_pop = pandasql.read_sql('''
                         SELECT * FROM cnangini.wp_pop
                         ''', con)
df_popd = pandasql.read_sql('''
                         SELECT * FROM cnangini.wp_popdensity
                         ''', con)

df_growth = pandasql.read_sql('''
                         SELECT * FROM cnangini.wp_growth
                         ''', con)

df_dow_ts = pandasql.read_sql('''
                         SELECT * FROM cnangini.wp_dow_timeseries
                         ''', con)

df_busiest_pudo_info = pandasql.read_sql('''
                         SELECT * FROM cnangini.wp_busiest_pudo_info
                         ''', con)

df_top5_dest = pandasql.read_sql('''
                         SELECT * FROM cnangini.wp_top5_dest
                         ''', con)

df_busiest_top5_dest = pandasql.read_sql('''
                         SELECT * FROM cnangini.wp_busiest_top5_dest
                         ''', con)

###################################################################################################
#                                                                                                 #
#                                        Constants                                                #
#                                                                                                 #
###################################################################################################

external_stylesheets = [dbc.themes.BOOTSTRAP]
# -----------------------------------------------------------------------
# Colour palettes
internal_external_colours = ['#410166', '#88639e'] # pickups, dropoffs
city_ward_colours = ['#660159','#7f7e7e'] #ward, city

# -----------------------------------------------------------------------
# Display dictionaries
ward_dict = {
    'w1': 'Etobicoke North', 'w2': 'Etobicoke Centre', 'w3': 'Etobicoke-Lakeshore',
    'w4': 'Parkdale-High Park', 'w5': 'York South-Weston', 'w6': 'York Centre',
    'w7': 'Humber River-Black Creek', 'w8': 'Eglinton-Lawrence', 'w9': 'Davenport',
    'w10': 'Spadina-Fort York', 'w11': 'University-Rosedale', 'w12': "Toronto-St. Paul's",
    'w13': 'Toronto Centre', 'w14': 'Toronto-Danforth', 'w15': 'Don Valley West',
    'w16': 'Don Valley East', 'w17': 'Don Valley North', 'w18': 'Willowdale',
    'w19': 'Beaches-East York', 'w20': 'Scarborough Southwest', 'w21': 'Scarborough Centre',
    'w22': 'Scarborough-Agincourt', 'w23': 'Scarborough North', 'w24': 'Scarborough-Guildwood',
    'w25': 'Scarborough-Rouge Park'
}

maptext_dict = {
    'w1': 'The largest hotspot is at Carlingview Drive & Dixon Rd around airport hotels. Other hotspots: Woodbine Racetrack and mall, Albion Centre mall, Toronto Congress Centre.',
    'w2': 'The largest hotspots are at offices along the 427, with other hotspots near apartment complexes (Eglinton & Kipling, Eglinton & Scarlett Rd, Markland & Humbertown).',
    'w3': 'Large hotspots at Sherway Gardens, Kipling & Islington stations, Humber Bay Shores; smaller clusters at Long Branch Loop, Humber Bay College, and condos along the QEW.',
    'w4': 'The map shows that activity is heavily concentrated in Parkdale, with other activity occurring near TTC stations along Bloor St, and in the Junction.',
    'w5': 'The map shows activity in the Stockyards and near Gunns Loop. Other hotspots cluster near the commercial centres and apartment/condo complexes around Weston Road.',
    'w6': 'The map shows the largest hotspot near Wilson station, with other clusters at Sheppard West station, and the Keele & Wilson area.',
    'w7': 'The largest cluster is near York University; other clusters near Seneca College/Sheridan Mall, Jane & Sheppard, and along Finch (e.g. Jane & Finch, Finch West station).',
    'w8': 'The map shows two major hotspots: one near Yorkdale mall, the other near Yonge & Eglinton, with smaller clusters along Lawrence, and around Forest Hill.',
    'w9': 'Major hotspots are clustered along Queen St W, with smaller clusters at Dufferin Mall/Dufferin station, Ossington station, and near Dupont/Lansdowne.',
    'w10': 'Major hotspots cluster near the Metro Convention Centre/CN Tower, Union station, King St West, Jack Layton Ferry Terminal, Billy Bishop Airport, and Liberty Village.',
    'w11': 'Activity was clustered around Little Italy, Bloor St in the Annex and Yorkville, and around the Discovery District.',
    'w12': 'Principal hotspots along Yonge St in Midtown near TTC stations. Other hotspots were at St. Clair West station and George Brown College.',
    'w13': 'The map shows activity at all parts of Yonge St, with other clusters along Church St, the Distillery District, and in St. Jamestown.',
    'w14': 'Activity occurred near Polson Pier, Queen & Broadview, along Carlaw Avenue/Gerrard Square, along Cosburn Avenue, and Broadview station.',
    'w15': 'Hotspots occurred at Thorncliffe Park, Yonge & Eglinton, Sunnybrook Hospital, Lawrence station, York Mills station, and York University Glendon.',
    'w16': 'Trips in this ward clustered at offices near Don Mills and Graydon Hall, and around Flemingdon Park.',
    'w17': 'Most trips clustered near the TTC stations along Sheppard Ave. Don Mills was the most active station, and around Victoria Park and Sheppard saw noticeable activity.',
    'w18': 'The map shows that trips clustered all along Yonge, with a main concentration around Finch station, and another near Sheppard-Yonge station.',
    'w19': 'The map shows that trips tended to cluster around TTC stations and near the apartment and condo buildings in Crescent Town.',
    'w20': 'The map shows that most trips tended to cluster along Eglinton Ave, with a major hotspot at Kennedy station.',
    'w21': 'The map shows major hotspots around Scarborough Centre station, with a smaller hotspot along Eglinton Avenue in the Golden Mile.',
    'w22': 'The map shows that hotspots tended to cluster along and around Sheppard Ave E, with another cluster e.g. near the Delta Hotels.',
    'w23': 'The map shows several hotspots around e.g. Sheppard & McCowan, and Markham Road south of Sheppard.',
    'w24': 'The map shows that trips tended to cluster at the eastern part of Scarborough Centre, with another cluster at Lawrence and Markham Road.',
    'w25': 'The map shows hotspot clusters around the University of Toronto Scarborough, and on Morningside at both Sheppard and Kingston Rd.'
}

# -----------------------------------------------------------------------
# App code
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dbc.Row(
        [
            dbc.Col([
                html.H1(
                    children='Ward Profile: ',
                    id='ward-title',
                    className='title'
                ),
                html.Div(
                    children='September 2018',
                    className='subtitle'
                )
            ], width=6, align="left"),

            dbc.Col([
                html.Img(
                    id='map-icon',
                    alt='Map of PTC activity'
            )], width=2),

            dbc.Col([
                html.Div([
                    html.Label('Select ward',id='dropdown-label'),
                        dcc.Dropdown(
                            id='ward-dropdown',
                            options=[
                                {'label': 'Etobicoke North', 'value': 'w1'},
                                {'label': 'Etobicoke Centre', 'value': 'w2'},
                                {'label': 'Etobicoke-Lakeshore', 'value': 'w3'},
                                {'label': 'Parkdale-High Park', 'value': 'w4'},
                                {'label': 'York South-Weston', 'value': 'w5'},
                                {'label': 'York Centre', 'value': 'w6'},
                                {'label': 'Humber River-Black Creek', 'value': 'w7'},
                                {'label': 'Eglinton-Lawrence', 'value': 'w8'},
                                {'label': 'Davenport', 'value': 'w9'},
                                {'label': 'Spadina-Fort York', 'value': 'w10'},
                                {'label': 'University-Rosedale', 'value': 'w11'},
                                {'label': "Toronto-St. Paul's", 'value': 'w12'},
                                {'label': 'Toronto Centre', 'value': 'w13'},
                                {'label': 'Toronto-Danforth', 'value': 'w14'},
                                {'label': 'Don Valley West', 'value': 'w15'},
                                {'label': 'Don Valley East', 'value': 'w16'},
                                {'label': 'Don Valley North', 'value': 'w17'},
                                {'label': 'Willowdale', 'value': 'w18'},
                                {'label': 'Beaches-East York', 'value': 'w19'},
                                {'label': 'Scarborough Southwest', 'value': 'w20'},
                                {'label': 'Scarborough Centre', 'value': 'w21'},
                                {'label': 'Scarborough-Agincourt', 'value': 'w22'},
                                {'label': 'Scarborough North', 'value': 'w23'},
                                {'label': 'Scarborough-Guildwood', 'value': 'w24'},
                                {'label': 'Scarborough-Rouge Park', 'value': 'w25'}
                            ],
                            value='w1'
                        )
                    ]
                )
        ], width=4, align="center")
    ]),

    #---------------------------------------------------------------------------
    # Orig/Dest maps
    dbc.Row(
        [
            dbc.Col([
                html.H3(
                    children='Ward at a Glance',
                    id='row1-col1-title',
                    className='myH3'
                )], width=4),

            dbc.Col([
                html.H3(
                    children='Top 20 Pick-up and Drop-off Hotspots',
                    id='row1-col2-title',
                    className='myH3'
            )], width=8)
        ]
    ),

    dbc.Row(
        [
            dbc.Col([
                html.Div(
                        children='',
                        id='dailytrip-value',
                        className='stats-label'
                ),
                html.Div(
                        children='',
                        id='vkt-value',
                        className='stats-label'
                ),
                html.Div(
                        children='',
                        id='pop_val',
                        className='stats-label'
                ),
                html.Div(
                        children='',
                        id='popdensity-value',
                        className='stats-label'
                )
            ], width=1, align="center"),

            dbc.Col([
                dcc.Graph(id='daily-trips-rank'),

                dcc.Graph(id='stats-pop'),

                dcc.Graph(id='stats-pop-density'),

                dcc.Graph(id='stats-pop-growth')

            ], width=3, align="left", className='lines-div'),

            dbc.Col([
                html.Img(
                    id='map-trips'
            )], width=8, className='tripmap-div')
        ]
    ),

    dbc.Row(
        [
            dbc.Col([
                html.Div(
                        children='Average trips/day',
                        id='dailytrip-title',
                        className='stats-title'
                ),
                html.Div(
                        children='Proportion of Traffic by PTCs',
                        id='pop-title',
                        className='stats-title'
                ),
                html.Div(
                        children='Population (2016)*',
                        id='popdensity-title',
                        className='stats-title'
                ),
                html.Div(
                        children='Population density per hectare (2016)*',
                        id='popgrowth-title',
                        className='stats-title'
                )], width=4, align="left", className='lines-div')
    ]),

    dbc.Row(
        [
            dbc.Col([
                html.Div(
                    children='*Source: Statistics Canada, Census 2016, 2011 & 2006.',
                    id='numberlines-caption',
                    className='caption'
            )], width=4),

            dbc.Col([
                html.Div(
                    children='',
                    id='map-caption',
                    className='caption'
            )], width=8)
        ]
    ),

    #---------------------------------------------------------------------------
    # Time series titles
    dbc.Row(
        [
            dbc.Col([
                html.H3(
                    children='Daily Trip Growth',
                    id='growth-title',
                    className='myH3'
            )], width=3),
            dbc.Col([
                html.H3(
                    children='Time of Week Profile',
                    id='dow-title',
                    className='myH3'
            )], width=9)
        ]
    ),
    #---------------------------------------------------------------------------
    # Time series graphs
    dbc.Row(
        [
            dbc.Col([
                html.Div(
                        children='',
                        id='growth-pc-ward',
                        className='pc-div'
                ),

                html.Div(
                        children='',
                        id='growth-pc-city',
                        className='pc-div'
                ),

                dcc.Graph(id='growth-bars'),

                html.Div(
                        children='Ward',
                        className='growth-barx1'
                ),
                html.Div(
                        children='City Avg',
                        className='growth-barx2'
                )
            ], width=3, align="center"),

            dbc.Col([
                dcc.Graph(id='dow-timeseries')
            ], width=9, align="center")
        ]
    ),
    #---------------------------------------------------------------------------
    # Time series captions
    dbc.Row(
        [
            dbc.Col([
                html.Div(
                children='* September Daily Average',
                className='growth-bar-footnote'
            )], width=3),
            dbc.Col([
                html.Div(
                    children='Mon',
                    id='dow-mon',
                    className='dow-label'
                ),
                html.Div(
                    children='Hour',
                    id='dow-hour',
                    className='dow-label'
                )
            ], width=1),
            dbc.Col([
                html.Div(
                    children='Tues',
                    id='dow-tue',
                    className='dow-label'
                )
            ], width=1),
            dbc.Col([
                html.Div(
                    children='Wed',
                    id='dow-wed',
                    className='dow-label'
                )
            ], width=1),
            dbc.Col([
                html.Div(
                    children='Thurs',
                    id='dow-thu',
                    className='dow-label'
                )
            ], width=1),
            dbc.Col([
                html.Div(
                    children='Fri',
                    id='dow-fri',
                    className='dow-label'
                )
            ], width=1),
            dbc.Col([
                html.Div(
                    children='Sat',
                    id='dow-sat',
                    className='dow-label'
                )
            ], width=1),
            dbc.Col([
                html.Div(
                    children='Sun',
                    id='dow-sun',
                    className='dow-label'
                )
            ], width=1)
        ]
    ),

    #---------------------------------------------------------------------------
    # Busiest hour
    dbc.Row(
        [
            dbc.Col([
                html.Div(
                    children='Five Busiest Locations',
                    id='daily-trips-title',
                    className='myH3'
                )
            ], width=4),

            dbc.Col([
                html.Div(
                    children='Busiest Hour (Sept 2016 – Sept 2018)',
                    className='myH3'
            ),
            html.Div(
                children='',
                id='busiest-title',
                className='busiest-subtitle'
            ),
            html.Div(
                children='',
                id='total-trips',
                className='busiest-subtitle'
            )], width=8)
        ]
    ),
    dbc.Row(
        [
            dbc.Col([
                html.Table(
                    children='',
                    id='top5-table'
                ),
                html.Div(
                    children='',
                    id='top5-caption',
                    className='caption'
                )
            ], width=4),

            dbc.Col([
                dcc.Graph(id='pie-fraction'),

                html.Div(
                    children='',
                    id='busiest-obs-caption',
                    className='caption'
                )
            ], width=4),

            dbc.Col([
                html.Table(
                    children='',
                    id='top5-busiest-table'
                )
            ], width=4)
        ]
    )
], className="container")

# -----------------------------------------------------------------------
# UI Handler - text updates for different sections
@app.callback(
    [dash.dependencies.Output('ward-title', 'children'),
    dash.dependencies.Output('dailytrip-value', 'children'),
    dash.dependencies.Output('vkt-value', 'children'),
    dash.dependencies.Output('pop_val', 'children'),
    dash.dependencies.Output('popdensity-value', 'children')],
    [dash.dependencies.Input('ward-dropdown', 'value')]
)
def update_stats(value):
    rank_val = df_rank.loc[df_rank['ward']==int(value[1:]), 'avg trips/day'].values[0]
    vkt_val = df_vkt.loc[df_vkt['ward']==int(value[1:]), 'prop_ptc_traffic'].values[0]
    pop_val = df_pop.loc[df_pop['ward']==int(value[1:]), 'pop'].values[0]
    popd_val = df_popd.loc[df_popd['ward']==int(value[1:]), 'pop_density'].values[0]

    return 'Ward {}'.format(value[1:] + ': ' + ward_dict[value]), \
    '{}'.format(rank_val), \
    '{}'.format(vkt_val + '%'), \
    '{}'.format(pop_val), \
    '{}'.format(popd_val)

@app.callback(
    dash.dependencies.Output('map-caption', 'children'),
    [dash.dependencies.Input('ward-dropdown', 'value')]
)
def update_mapcaption(value):
    return '{}'.format(maptext_dict[value])

@app.callback(
    [dash.dependencies.Output('growth-pc-ward', 'children'),
     dash.dependencies.Output('growth-pc-city', 'children')],
    [dash.dependencies.Input('ward-dropdown', 'value')]
)
def update_growth(value):
    # Percent growth change in ward and in city
    grow_pcval_ward = '+' + repr(df_growth.loc[df_growth['ward']==value, 'percent_change'].values[0]) + '%'
    grow_pcval_city = '+' + repr(df_growth.loc[df_growth['ward']=='city', 'percent_change'].values[0]) + '%'

    return '{}'.format(grow_pcval_ward), \
    '{}'.format(grow_pcval_city)

@app.callback(
    [dash.dependencies.Output('top5-caption', 'children'),
     dash.dependencies.Output('busiest-title', 'children'),
     dash.dependencies.Output('total-trips', 'children'),
     dash.dependencies.Output('busiest-obs-caption', 'children')],
    [dash.dependencies.Input('ward-dropdown', 'value')]
)
def update_busy_texts(value):
    # Busiest hour texts
    busiest_hr = df_busiest_pudo_info.loc[df_busiest_pudo_info['ward']==value, 'div1'].values[0]
    busiest_tot = df_busiest_pudo_info.loc[df_busiest_pudo_info['ward']==value, 'div2'].values[0]
    busiest_obs = df_busiest_pudo_info.loc[df_busiest_pudo_info['ward']==value, 'Observations'].values[0]
    busiest_top5 = df_top5_dest.loc[df_top5_dest['ward']==value, 'Observations'].values[0]

    return '{}'.format(busiest_top5), \
    '{}'.format(busiest_hr), \
    '{}'.format(busiest_tot), \
    '{}'.format(busiest_obs)

# -----------------------------------------------------------------------
# ** Map icon inset **
def display_map_icon(value):
    image_icon = 'img/inset/inset_' + value + '.png'
    encoded_icon = base64.b64encode(open(image_icon, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded_icon.decode())

# -----------------------------------------------------------------------
# WARD PROFILE
# ** Avg trips/day ranking number line **
def create_daily_rank_scatter(value):
    return {
        'data': [
            go.Scatter(
                x=df_rank['avg trips/day'],
                y=df_rank['y'],
                mode='markers',
                marker= {
                    'opacity': 1,
                    'size': 14,
                    'color': city_ward_colours[1],
                    'line': {'width': 1, 'color': 'white'}
                },
                name='other wards'
            ),
            # ward
            go.Scatter(
                x=df_rank.loc[df_rank['ward']==int(value[1:]), 'avg trips/day'],
                y=df_rank['y'],
                mode='markers',
                marker= {
                    'opacity': 1,
                    'size': 14,
                    'color': city_ward_colours[0],
                    'line': {'width': 3, 'color': 'white'}
                },
                name='Ward ' + value[1:]
            )
        ],
        'layout': {
            'height': 200,
            'margin': {'l': 0, 'b': 80, 'r': 14, 't': 0},
            'titlefont': {
                'family': 'Libre Franklin, sans-serif',
                'size': '14',
                'weight': 700
             },
            'xaxis' :{
                'ticks': 'outside',
                'dtick': 6000,
                'showticklabels': True,
                'showgrid':False,
                'zeroline':True,
                'showline': True,
                'zerolinecolor': '#969696',
                'zerolinewidth':4
            },
            'yaxis': {
                # 'range': [-0.01, 0.01],
                'showticklabels': False,
                'showgrid':False,
                'showline': False
            },
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': 1, 'x':0}
        }
}

# ** ward pop number line **
def create_pop_scatter(value):
    return {
        'data': [
            go.Scatter(
                x=df_vkt['prop_ptc_traffic'],
                y=df_vkt['y'],
                mode='markers',
                marker= {
                    'opacity': 1,
                    'size': 14,
                    'color': city_ward_colours[1],
                    'line': {'width': 1, 'color': 'white'}
                },
                name='other wards'
            ),
            go.Scatter(
                x=df_vkt.loc[df_vkt['ward']==int(value[1:]), 'prop_ptc_traffic'],
                y=df_vkt['y'],
                mode='markers',
                marker= {
                    'opacity': 1,
                    'size': 14,
                    'color': city_ward_colours[0],
                    'line': {'width': 3, 'color': 'white'}
                },
                name=ward_dict[value]
            )
        ],
        'layout': {
            'height': 200,
            'margin': {'l': 0, 'b': 80, 'r': 14, 't': 0},
            'titlefont': {
                'family': 'Libre Franklin, sans-serif',
                'size': '14',
                'weight': 700
             },
            'xaxis' :{
                'ticks': 'outside',
                'dtick': 2,
                'showticklabels': True,
                'showgrid':False,
                'zeroline':True,
                'showline': True,
                'zerolinecolor': '#969696',
                'zerolinewidth':4
            },
            'yaxis': {
                'showticklabels': False,
                'showgrid':False,
                'showline': False
            },
            'showlegend': False,
            'legend': {'orientation': 'h', 'y': .8, 'x':0}
        }
    }

# ** ward pop density number line **
def create_pop_density_scatter(value):
    return {
        'data': [
            go.Scatter(
                x=df_pop['pop'],
                y=df_pop['y'],
                mode='markers',
                marker= {
                    'opacity': 1,
                    'size': 14,
                    'color': city_ward_colours[1],
                    'line': {'width': 1, 'color': 'white'}
                },
                name='other wards'
            ),
            go.Scatter(
                x=df_pop.loc[df_pop['ward']==int(value[1:]), 'pop'],
                y=df_pop['y'],
                mode='markers',
                marker= {
                    'opacity': 1,
                    'size': 14,
                    'color': city_ward_colours[0],
                    'line': {'width': 3, 'color': 'white'}
                },
                name=ward_dict[value]
            )
        ],
        'layout': {
            'height': 200,
            'margin': {'l': 0, 'b': 80, 'r': 14, 't': 0},
            'titlefont': {
                'family': 'Libre Franklin, sans-serif',
                'size': '14',
                'weight': 700
             },
            'xaxis' :{
                'ticks': 'outside',
                'dtick': 8000,
                'showticklabels': True,
                'showgrid':False,
                'zeroline':True,
                'showline': True,
                'zerolinecolor': '#969696',
                'zerolinewidth':4
            },
            'yaxis': {
                'showticklabels': False,
                'showgrid':False,
                'showline': False
            },
            'showlegend': False,
            'legend': {'orientation': 'h', 'y': .8, 'x':0}
        }
    }

# ** ward pop growth number line **
def create_pop_density_scatter(value):
    return {
        'data': [
            go.Scatter(
                x=df_popd['pop_density'],
                y=df_popd['y'],
                mode='markers',
                marker= {
                    'opacity': 1,
                    'size': 14,
                    'color': city_ward_colours[1],
                    'line': {'width': 1, 'color': 'white'}
                },
                name='other wards'
            ),
            go.Scatter(
                x=df_popd.loc[df_popd['ward']==int(value[1:]), 'pop_density'],
                y=df_popd['y'],
                mode='markers',
                marker= {
                    'opacity': 1,
                    'size': 14,
                    'color': city_ward_colours[0],
                    'line': {'width': 3, 'color': 'white'}
                },
                name=ward_dict[value]
            )
        ],
        'layout': {
            'height': 200,
            'margin': {'l': 0, 'b': 80, 'r': 14, 't': 0},
            'titlefont': {
                'family': 'Libre Franklin, sans-serif',
                'size': '14',
                'weight': 700
             },
            'xaxis' :{
                'ticks': 'outside',
                'dtick': 50,
                'showticklabels': True,
                'showgrid':False,
                'zeroline':True,
                'showline': True,
                'zerolinecolor': '#969696',
                'zerolinewidth':4
            },
            'yaxis': {
                'showticklabels': False,
                'showgrid':False,
                'showline': False
            },
            'showlegend': False,
            'legend': {'orientation': 'h', 'y': .8, 'x':0}
        }
    }

# ** Trip map **
def display_tripmap(value):
    image_tripmap = 'img/' + value + '-tripmap.jpeg'
    encoded_tripmap = base64.b64encode(open(image_tripmap, 'rb').read())
    return 'data:image/jpeg;base64,{}'.format(encoded_tripmap.decode())

# ** Growth bar chart **
def create_growth_bars(value):
    ward_val_2016 = df_growth.loc[df_growth['ward']==value,'Sept2016'].values[0]
    ward_val_2018 = df_growth.loc[df_growth['ward']==value,'Sept2018'].values[0]

    city_val_2016 = df_growth.loc[df_growth['ward']=='city','Sept2016'].values[0]
    city_val_2018 = df_growth.loc[df_growth['ward']=='city','Sept2018'].values[0]

    trace1 = go.Bar(
            x=['2016*     2018*', '2016*     2018*      .'],
            y=[ward_val_2016, city_val_2016],
            text=[repr(round(ward_val_2016, -2)/1000)+'k', repr(round(city_val_2016, -2)/1000)+'k'],
            textposition = 'auto',
            textfont= {
                'size': 14,
                # 'color': 'white'
            },
            name='Sept 2016'
        )
    trace2 = go.Bar(
        x=['2016*     2018*', '2016*     2018*      .'],
        y=[ward_val_2018, city_val_2018],
        text=[repr(round(ward_val_2018, -2)/1000)+'k', repr(round(city_val_2018, -2)/1000)+'k'],
        textposition = 'auto',
        textfont= {
            'size': 14,
            'color': 'white'
        },
        name='Sept 2018'
    )
    return {
        'data': [trace1, trace2],
        'layout': {
            'height': 175,
            'margin': {'l': 0, 'b': 20, 'r': 0, 't': 0},
            'barmode': 'group',
            'showlegend': False,
            'legend': {'orientation': 'h'},
            'yaxis': {
                'tickformat': 's'
            }
        }
    }

# ** Day of Week time series **
def create_dow_timeseries(value):
    index = list(df_dow_ts.index)
    # x-axis tick labels
    # divide 24h into a time chunk of interest (6h)
    dt = 6
    # print every dt-th value of index for the tick values
    this_tickvals = index[::dt]
    # number of cycles given chosen dt
    num_cycles = int(len(this_tickvals)/int(24/dt))
    this_ticktext = list(range(23))[::dt] * num_cycles # ['0','6','12','18','0','6','12','18'...] repeated by num_cycles

    return {
        'data': [
            go.Scatter(
                x=index,
                y=df_dow_ts['city'].values,
                mode='lines',
                line={'color': city_ward_colours[1], 'width': 2},
                name='City'
            ),
            # ward
            go.Scatter(
                x=index,
                y=df_dow_ts[value].values,
                mode='lines',
                line={'color': city_ward_colours[0], 'width': 4},
                name=ward_dict[value]
            )
        ],
        'layout': {
            'height': 200,
            'margin': {'l': 30, 'b': 60, 'r': 10, 't': 0},
            'annotations': [{
                'x': 0, 'y': 0.90, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left',
                'text': 'Trip fraction (%)'
            }],
            'yaxis': {
                'type': 'linear',
                'showline': True,
                'tickcolor': '#000'
            },
            'xaxis': {
                'showgrid': False,
                'ticks': 'outside',
                'showticklabels': True,
                'showline': True,
                'ticktext': this_ticktext,
                'tickvals': this_tickvals
            },
            'showlegend': True,
            'legend': {'orientation': 'h', 'y': 15, 'x':0}
        }
    }
# ==============================================================================
# ** Function to make the 2 top5 destination tables
# (in `create_top5_table` and `create_busiest_top5_dest_table`)
def make_table(this_ward,table_cols,df):
    """
    Creates the top5 destination tables.
    Inputs:
    this_ward: value from drop-down menu
    table_cols: columns of table to be created
    df: input df from EC2 used to create the output table

    Outputs:
    df_table
    """
    df_table = pd.DataFrame(columns=table_cols)

    # Store values for first column of df_table in an array
    # Note col0 is the ward
    d1 = df.loc[df['ward']==this_ward, df.columns[1]].values[0]
    d2 = df.loc[df['ward']==this_ward, df.columns[2]].values[0]
    d3 = df.loc[df['ward']==this_ward, df.columns[3]].values[0]
    d4 = df.loc[df['ward']==this_ward, df.columns[4]].values[0]
    d5 = df.loc[df['ward']==this_ward, df.columns[5]].values[0]
    d_arr = [d1, d2, d3, d4, d5]

    # Store values for second column of df_table in an array
    t1 = df.loc[df['ward']==this_ward, df.columns[6]].values[0]
    t2 = df.loc[df['ward']==this_ward, df.columns[7]].values[0]
    t3 = df.loc[df['ward']==this_ward, df.columns[8]].values[0]
    t4 = df.loc[df['ward']==this_ward, df.columns[9]].values[0]
    t5 = df.loc[df['ward']==this_ward, df.columns[10]].values[0]
    t_arr = [t1, t2, t3, t4, t5]

    # Store values for third column of df_table in an array
    f1 = df.loc[df['ward']==this_ward, df.columns[11]].values[0]
    f2 = df.loc[df['ward']==this_ward, df.columns[12]].values[0]
    f3 = df.loc[df['ward']==this_ward, df.columns[13]].values[0]
    f4 = df.loc[df['ward']==this_ward, df.columns[14]].values[0]
    f5 = df.loc[df['ward']==this_ward, df.columns[15]].values[0]
    f_arr = [f1, f2, f3, f4, f5]

    # Assemble output table
    df_table = pd.DataFrame(columns=table_cols)
    df_table[table_cols[0]] = d_arr
    df_table[table_cols[1]] = t_arr
    df_table[table_cols[2]] = f_arr

    return df_table
# ==============================================================================

# ** Top-5 destinations table **
def create_top5_table(value):
    # Create the table à la volée
    table_cols = ['Destination', 'Trips/day', 'Fraction (%)']
    df_dest_table = make_table(value,table_cols,df_top5_dest)

    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in table_cols])] +

        # Body
        [html.Tr([
            html.Td(
            df_dest_table.iloc[i][col]
            ) for col in table_cols
        ]) for i in range(len(df_dest_table))]
    )

# BUSIEST HOUR
# ** Pie fraction **
def create_pie_fraction(value):
    pu = df_busiest_pudo_info.loc[df_busiest_pudo_info['ward']==value, 'Pickups'].values[0]
    do = df_busiest_pudo_info.loc[df_busiest_pudo_info['ward']==value, 'Dropoffs'].values[0]
    return {
        'data': [
            go.Pie(
                labels=['Pickups', 'Dropoffs'],
                values=[pu, do],
                hoverinfo='label+percent', textinfo='value',
                marker=dict(
                    colors=internal_external_colours
                ),
                textfont= {
                    'size': 16,
                    'color': 'white'
                }
            )
        ],
        'layout': {
            'height': 120,
            'margin': {'l': 0, 'b': 0, 'r': 0, 't': 0}

        }
    }

# ** Busiest hour info table **
def create_busiest_top5_dest_table(value):
    # Create the table à la volée
    table2_cols = ['Top 5 Destinations', 'Trips', '%']
    df_dest_table2 = make_table(value,table2_cols,df_busiest_top5_dest)

    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in table2_cols])] +

        # Body
        [html.Tr([
            html.Td(
            df_dest_table2.iloc[i][col]
            ) for col in table2_cols
        ]) for i in range(len(df_dest_table2))]
    )

# ------------------------------------------------------------------------------
# Update charts after menu selection

# ** map icon **
@app.callback(
 dash.dependencies.Output('map-icon', 'src'),
 [dash.dependencies.Input('ward-dropdown', 'value')]
 )
def update_display_map_icon(value):
    return display_map_icon(value)

# WARD PROFILE SECTION
# ** avg trips/day **
@app.callback(
 dash.dependencies.Output('daily-trips-rank', 'figure'),
 [dash.dependencies.Input('ward-dropdown', 'value')]
 )
def update_daily_rank_scatter(value):
    return create_daily_rank_scatter(value)
# ** ward pop **
@app.callback(
 dash.dependencies.Output('stats-pop', 'figure'),
 [dash.dependencies.Input('ward-dropdown', 'value')]
 )
def update_ward_pop(value):
    return create_pop_scatter(value)
# ** ward pop density **
@app.callback(
 dash.dependencies.Output('stats-pop-density', 'figure'),
 [dash.dependencies.Input('ward-dropdown', 'value')]
 )
def update_ward_pop_density(value):
    return create_pop_density_scatter(value)
# ** ward pop density **
@app.callback(
 dash.dependencies.Output('stats-pop-growth', 'figure'),
 [dash.dependencies.Input('ward-dropdown', 'value')]
 )
def update_ward_pop_density(value):
    return create_pop_density_scatter(value)

# ** trip map **
@app.callback(
 dash.dependencies.Output('map-trips', 'src'),
 [dash.dependencies.Input('ward-dropdown', 'value')]
 )
def update_display_maps(value):
    return display_tripmap(value)

# ** top-5 destinations table **
@app.callback(
 dash.dependencies.Output('top5-table', 'children'),
 [dash.dependencies.Input('ward-dropdown', 'value')]
 )
def update_top5_table(value):
    return create_top5_table(value)

# ** growth ts **
@app.callback(
 dash.dependencies.Output('growth-bars', 'figure'),
 [dash.dependencies.Input('ward-dropdown', 'value')]
 )
def update_growth_bars(value):
    return create_growth_bars(value)

# ** dow ts **
@app.callback(
 dash.dependencies.Output('dow-timeseries', 'figure'),
 [dash.dependencies.Input('ward-dropdown', 'value')]
 )
def update_growth_timeseries(value):
    return create_dow_timeseries(value)

# ** pickups vs dropoffs fraction pie chart **
@app.callback(
 dash.dependencies.Output('pie-fraction', 'figure'),
 [dash.dependencies.Input('ward-dropdown', 'value')]
 )
def update_pie_fraction(value):
    return create_pie_fraction(value)

# ** busiest hour top5-destinations table **
@app.callback(
 dash.dependencies.Output('top5-busiest-table', 'children'),
 [dash.dependencies.Input('ward-dropdown', 'value')]
 )
def update_busiest_info_table(value):
    return create_busiest_top5_dest_table(value)


if __name__ == '__main__':
    app.run_server(debug=True)
