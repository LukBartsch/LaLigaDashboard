import requests
import os

#from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By

from dash import Dash, dash_table, html, dcc, Input, Output, callback#, DiskcacheManager, CeleryManager#, set_props
import dash_bootstrap_components as dbc
from bs4 import BeautifulSoup
import pandas as pd

from common import url as URL, raw_url as RAW_URL

from data_manage import get_current_season_number, get_older_seasons, set_default_season_list, \
                        get_head_row, get_tooltips_row, get_body_rows, get_zone_explanation, \
                        get_league_header, clean_list, set_legend_colors, set_main_table_position_colors, \
                        get_lists_with_top_players, prepare_data_about_top_players_for_datatable, \
                        get_stats_column, get_ovierview_column




tab_style = {
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': '#ffffff',
        'height': '58px',
        'padding': '15px',
}

tab_selected_style = {
        'backgroundColor': '#111111',
        'borderLeft': '2px solid #007eff',
        'color': '#007eff',
        'height': '58px',
        'padding': '15px',
}



# if "REDIS_URL" in os.environ:
#     # Use Redis & Celery if REDIS_URL set as an env variable
#     from celery import Celery

#     celery_app = Celery(
#         __name__, broker=os.environ["REDIS_URL"], backend=os.environ["REDIS_URL"]
#     )
#     background_callback_manager = CeleryManager(celery_app)

# else:
#     # Diskcache for non-production apps when developing locally
#     import diskcache

#     cache = diskcache.Cache("./cache")
#     background_callback_manager = DiskcacheManager(cache)



app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) #background_callback_manager=background_callback_manager


app.layout = dbc.Container([

                dbc.Row(
                        [
                            dbc.Col(
                                dcc.Dropdown(
                                    id = 'select-season-dropdown',
                                    options = set_default_season_list(),
                                    value = "0",
                                    clearable = False,
                                    style = {
                                        'marginTop': '20px',
                                    }
                                ),
                            ),
                            dbc.Col(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Button(id="button_id", children="Get older seasons data", color="dark", disabled=True, style={'width': '300px', 'outline': 'white solid 1px'}),
                                            ),

                                            dbc.Col(
                                                dbc.Button(id="cancel_button_id", children="Cancel getting data", color="dark", disabled=True, style={'width': '300px', 'outline': 'white solid 1px'}),
                                            )

                                        ],
                                        style = {
                                            'marginTop': '20px',
                                    }),

                                    dbc.Row(
                                        html.Progress(id="progress_bar", value="0", style={"visibility": "hidden"}),
                                        style = {
                                            'marginTop': '10px',
                                            'marginLeft': '5px',
                                            'marginRight': '10px',
                                            }
                                    )   
                                    
                                ]
                            ),
                        ]
                    ), 

                dbc.Row([
                    dbc.Col(
                        dbc.Row([
                            dbc.Col(
                                id='league-logo',
                            ),
                            dbc.Col(
                                id='league-header',
                            )
                        ]),
                        width = 4
                    ),
                    dbc.Col(
                        id='tabs-menu',
                    )
                ]),
                dbc.Row([
                    dbc.Col(
                        id='table-title',    
                    ),
                    dbc.Spinner(
                        dbc.Col(
                            id='main-table',
                        ),
                        color="primary",
                        spinner_style={"width": "3rem", "height": "3rem", "marginTop": "150px"}
                    ),
                    dbc.Col(
                        id='main-table-legend',
                    )]
                )
            ])



@callback(
    Output('league-logo', 'children'),
    Output('league-header', 'children'),
    Output('tabs-menu', 'children'),
    Output('table-title', 'children'),
    Output('main-table', 'children'),
    Output('main-table-legend', 'children'),
    Input('select-season-dropdown', 'value'),
)
def update_season(value):


    if value == "0":

        response = requests.get(URL)
        soup = BeautifulSoup(response.text, 'html.parser')

    else:

        with open(f"static\\stats\\season_{value}.html", encoding="utf-8") as f:
              contents = f.read()

        soup = BeautifulSoup(contents, 'html.parser')



    table_title = soup.find ('div', {'class':'normalContentWidth cf leagueStatsTable'}).text.strip()

    main_table = soup.find ('table', {'class':'full-league-table table-sort col-sm-12 mobify-table'}).thead
    main_table_head = main_table.find_all ('th')

    try:
        head_row = get_head_row(main_table_head)
    except:
        head_row = []


    # print(head_row)
    # print(len(head_row))

    try:
        tooltips_head_row = get_tooltips_row(main_table_head)
    except:
        tooltips_head_row = []


    # print(tooltips_head_row)
    # print(len(tooltips_head_row))


    main_table = soup.find ('table', {'class':'full-league-table table-sort col-sm-12 mobify-table'}).tbody
    main_table_body = main_table.find_all('tr')

    try:
        body_rows = get_body_rows(main_table_body)
    except:
        body_rows = []

    # print(body_rows[0])
    # print(len(body_rows))

    try:
        df = pd.DataFrame(body_rows, columns = head_row)

        df.drop('YC', inplace=True, axis=1)
        df.drop('Cor', inplace=True, axis=1)


        data=df.to_dict("records")
        columns = [{"name": i, "id": i} for i in df.columns]
        columns[1].update({"presentation": "markdown"})
        columns[11].update({"name": "Last 5"})
        columns[12].update({"name": "Last 5"})
        columns[13].update({"name": "Last 5"})
        columns[14].update({"name": "Last 5"})
        columns[15].update({"name": "Last 5"})

        tooltip_dict = dict(zip(head_row, tooltips_head_row))

    except:
        df = pd.DataFrame()
        data=df.to_dict("records")
        columns = [{"name": i, "id": i} for i in df.columns]
        tooltip_dict = dict(zip(head_row, tooltips_head_row))



    zone_explanation = soup.find ('ul', {'class':'zone-explanation'})
    zone_explanation_list = zone_explanation.find_all('li')

    try:
        main_table_legend = get_zone_explanation(zone_explanation_list)

        legend_colors = set_legend_colors(len(main_table_legend))
        champions_league_colors, europa_league_colors, europa_league_qualifiers_colors, relegation_colors = set_main_table_position_colors(len(main_table_legend), value)

        df_legend = pd.DataFrame(main_table_legend, columns=["Col", "Description"])
        legend_data=df_legend.to_dict("records")
        legend_columns = [{"name": i, "id": i} for i in df_legend.columns]

    except:
        main_table_legend = []
        df_legend = pd.DataFrame()
        legend_data=df_legend.to_dict("records")
        legend_columns = [{"name": i, "id": i} for i in df_legend.columns]


    try: 
        league_header = soup.find ('div', {'class':'first cf'})
        league_header_img = league_header.find ('img', {'class':'teamCrest'}).get('src')
        league_logo= html.Img(src=league_header_img, 
                            width="180", 
                            height="180", 
                            style={
                                'marginTop': '30px'
                            })


        league_header_first_col = league_header.find_all('div', {'class':'w35 fl'})
        league_header_first_col_list = get_league_header(league_header_first_col)

        # print(league_header_first_col_list)

        league_header_second_col = league_header.find_all('div', {'class':'fl'})
        league_header_second_col_list = get_league_header(league_header_second_col)
        league_header_second_col_list = clean_list(league_header_first_col_list, league_header_second_col_list)

        # print(league_header_second_col_list)


        if len(league_header_first_col_list) > 6:
            league_header_first_col_list = league_header_first_col_list[:6]
            league_header_second_col_list[5] = '100%'

        if len(league_header_second_col_list) > 6:
            league_header_second_col_list = league_header_second_col_list[:6]
            league_header_second_col_list[5] = '100%'


        df_league_header = pd.DataFrame(data = [league_header_first_col_list, league_header_second_col_list], columns=["1", "2", "3", "4", "5", "6"])

        df_league_header = df_league_header.transpose()
        df_league_header.columns=["1", "2"]
        league_header_data=df_league_header.to_dict("records")
        league_header_columns = [{"name": i, "id": i} for i in df_league_header.columns]

    except:
        df_league_header = pd.DataFrame()
        league_header_data=df_league_header.to_dict("records")
        league_header_columns = [{"name": i, "id": i} for i in df_league_header.columns]


    

    try:
        top_scorers = soup.find_all('div', {'class':'w90 m0Auto pb1e'})

        top_scorers_name_list, top_scorers_value_list = get_lists_with_top_players(top_scorers[0], value)
        top_assists_name_list, top_assists_value_list = get_lists_with_top_players(top_scorers[1], value)
        clean_sheets_name_list, clean_sheets_value_list = get_lists_with_top_players(top_scorers[2], value)


        top_scorers_columns, top_scorers_data_first_col, top_scorers_data_second_col = prepare_data_about_top_players_for_datatable(top_scorers_name_list, top_scorers_value_list)
        top_assists_columns, top_assists_data_first_col, top_assists_data_second_col = prepare_data_about_top_players_for_datatable(top_assists_name_list, top_assists_value_list)
        clean_sheets_columns, clean_sheets_data_first_col, clean_sheets_data_second_col = prepare_data_about_top_players_for_datatable(clean_sheets_name_list, clean_sheets_value_list)

    except:

        top_scorers_columns = [] 
        top_scorers_data_first_col = {}
        top_scorers_data_second_col = {}

        top_assists_columns = []
        top_assists_data_first_col = {}
        top_assists_data_second_col = {}

        clean_sheets_columns = []
        clean_sheets_data_first_col = {}
        clean_sheets_data_second_col = {}


    stats_columns, data_stats = get_stats_column(soup)
    overview_columns, data_overview = get_ovierview_column(soup)



    main_table = dash_table.DataTable(
                        data, 
                        columns,
                        tooltip_header=tooltip_dict,
                        export_headers='display',
                        fill_width=False,
                        merge_duplicate_headers=True,
                        style_header={
                            'backgroundColor': 'rgb(30, 30, 30)',
                            'color': '#007eff',
                            'textAlign': 'center',
                            'fontWeight': 'bold',
                            'fontSize': '20px',
                            'height': '40px',
                            'textDecoration': 'underline',
                            'textDecorationStyle': 'dotted',
                        },
                        style_cell={
                            'padding-right': '10px',
                            'padding-left': '10px',
                            'text-align': 'center',
                            'marginLeft': 'auto',
                            'marginRight': 'auto',
                            'backgroundColor': '#111111',
                            'color': '#ffffff'
                        },
                        css=[{
                            'selector': '.dash-spreadsheet td div',
                            'rule': '''
                                line-height: 15px;
                                max-height: 30px; min-height: 30px; height: 30px;
                                overflow-y: hidden;
                            '''
                        }],
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(30, 30, 30)',
                            },
                            {
                                'if': {'column_id': 'GF'},
                                'color': '#2E8B57',
                            },
                            {
                                'if': {'column_id': 'GA'},
                                'color': 'tomato',
                            },
                            {
                                'if': {'column_id': 'Pts'},
                                'fontWeight': 'bold',
                                'outline': '1px solid white',
                                'outline-offset': '-7px'
                            },
                            {
                                'if': {
                                    'filter_query': '{PPG} > 2',
                                    'column_id': 'PPG'
                                },
                                'backgroundColor': '#2E8B57',
                            },
                            {
                                'if': {
                                    'filter_query': '{PPG} > 1.5 && {PPG} <= 2' ,
                                    'column_id': 'PPG'
                                },
                                'backgroundColor': '#91BC80',
                            },
                            {
                                'if': {
                                    'filter_query': '{PPG} > 1.1 && {PPG} <= 1.5' ,
                                    'column_id': 'PPG'
                                },
                                'backgroundColor': '#E5B05E',
                            },
                            {
                                'if': {
                                    'filter_query': '{PPG} <= 1.1' ,
                                    'column_id': 'PPG'
                                },
                                'backgroundColor': '#C85F46',
                            },
                            champions_league_colors,
                            europa_league_colors,
                            europa_league_qualifiers_colors,
                            relegation_colors,
                            {
                                'if': {
                                    'filter_query': '{1} contains "W"',
                                    'column_id': '1'
                                },
                                'color': '#68AA80',
                            },
                            {
                                'if': {
                                    'filter_query': '{2} contains "W"',
                                    'column_id': '2'
                                },
                                'color': '#68AA80',
                            },
                            {
                                'if': {
                                    'filter_query': '{3} contains "W"',
                                    'column_id': '3'
                                },
                                'color': '#68AA80',
                            },
                            {
                                'if': {
                                    'filter_query': '{4} contains "W"',
                                    'column_id': '4'
                                },
                                'color': '#68AA80',
                            },
                            {
                                'if': {
                                    'filter_query': '{5} contains "W"',
                                    'column_id': '5'
                                },
                                'color': '#68AA80',
                            },
                            {
                                'if': {
                                    'filter_query': '{1} contains "D"',
                                    'column_id': '1'
                                },
                                'color': '#E5B05E',
                            },
                            {
                                'if': {
                                    'filter_query': '{2} contains "D"',
                                    'column_id': '2'
                                },
                                'color': '#E5B05E',
                            },
                            {
                                'if': {
                                    'filter_query': '{3} contains "D"',
                                    'column_id': '3'
                                },
                                'color': '#E5B05E',
                            },
                            {
                                'if': {
                                    'filter_query': '{4} contains "D"',
                                    'column_id': '4'
                                },
                                'color': '#E5B05E',
                            },
                            {
                                'if': {
                                    'filter_query': '{5} contains "D"',
                                    'column_id': '5'
                                },
                                'color': '#E5B05E',
                            },
                            {
                                'if': {
                                    'filter_query': '{1} contains "L"',
                                    'column_id': '1'
                                },
                                'color': '#BB5555',
                            },
                            {
                                'if': {
                                    'filter_query': '{2} contains "L"',
                                    'column_id': '2'
                                },
                                'color': '#BB5555',
                            },
                            {
                                'if': {
                                    'filter_query': '{3} contains "L"',
                                    'column_id': '3'
                                },
                                'color': '#BB5555',
                            },
                            {
                                'if': {
                                    'filter_query': '{4} contains "L"',
                                    'column_id': '4'
                                },
                                'color': '#BB5555',
                            },
                            {
                                'if': {
                                    'filter_query': '{5} contains "L"',
                                    'column_id': '5'
                                },
                                'color': '#BB5555',
                            },
                            {
                                'if': {'column_id': 'Logo'},
                                'padding-left': '16px',
                            }
                        ],
                        tooltip_delay=0,
                        tooltip_duration=None
                    )

    table_title = html.H2(
                        table_title,
                        style={
                            'text-align': 'center',
                            'marginLeft': 'auto',
                            'marginRight': 'auto',
                            'padding': '10px',
                            'color': '#ffffff'
                        })

    main_table_legend = dash_table.DataTable(
                        legend_data, 
                        legend_columns,
                        fill_width=False,
                        style_header = {'display': 'none'},
                        style_cell={
                            'backgroundColor': '#111111',
                            'color': '#ffffff'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'Col'},
                                'width': '40px'
                            },
                            {
                                'if': {'column_id': 'Description'},
                                'padding-right': '10px',
                                'padding-left': '10px',
                                'text-align': 'left',
                            },
                        ],
                        style_data_conditional = legend_colors,
                        style_table={
                            'margin-bottom': '30px',
                        },
                    )

    league_header = dash_table.DataTable(
                        league_header_data, 
                        league_header_columns,
                        fill_width=False,
                        style_header = {'display': 'none'},
                        style_cell={
                            'backgroundColor': '#111111',
                            'color': '#ffffff'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': ['1', '2']},
                                'padding-right': '10px',
                                'padding-left': '10px',
                                'text-align': 'left',
                            },
                            {
                                'if': {'column_id': '2'},
                                'color': '#007eff',
                            }
                        ],
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(30, 30, 30)',
                            }
                        ]
                    )





    #TODO: ONLY EXAMPLE
    overview_table = dash_table.DataTable(
                        data_overview,
                        overview_columns,
                        style_header = {'display': 'none'},
                        style_cell={
                            'backgroundColor': '#111111',
                            'color': '#ffffff'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': ['Parameter', 'Value']},
                                'padding-right': '10px',
                                'padding-left': '10px',
                                'text-align': 'center',
                            },
                            {
                                'if': {'column_id': 'Parameter'},
                                'color': '#007eff',
                            }
                        ],
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(30, 30, 30)',
                            }
                        ]
    )
    #TODO: ONLY EXAMPLE
    stats_table = dash_table.DataTable(
                        data_stats,
                        stats_columns,
                        style_header = {'display': 'none'},
                        style_cell={
                            'backgroundColor': '#111111',
                            'color': '#ffffff'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': ['Parameter', 'Value']},
                                'padding-right': '10px',
                                'padding-left': '10px',
                                'text-align': 'center',
                            },
                            {
                                'if': {'column_id': 'Parameter'},
                                'color': '#007eff',
                            }
                        ],
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(30, 30, 30)',
                            }
                        ]
    )



    top_scorers_first_table = dash_table.DataTable(
                        top_scorers_data_first_col,
                        top_scorers_columns,
                        style_header = {'display': 'none'},
                        style_cell={
                            'backgroundColor': '#111111',
                            'color': '#ffffff'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': ['Position', 'Parameter', 'Value']},
                                'padding-right': '10px',
                                'padding-left': '10px',
                                'text-align': 'center',
                            },
                            {
                                'if': {'column_id': ['Value']},
                                'color': '#007eff',
                            }
                        ],
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(30, 30, 30)',
                            }
                        ]
    )
    top_scorers_second_table = dash_table.DataTable(
                        top_scorers_data_second_col,
                        top_scorers_columns,
                        style_header = {'display': 'none'},
                        style_cell={
                            'backgroundColor': '#111111',
                            'color': '#ffffff'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': ['Position', 'Parameter', 'Value']},
                                'padding-right': '10px',
                                'padding-left': '10px',
                                'text-align': 'center',
                            },
                            {
                                'if': {'column_id': ['Value']},
                                'color': '#007eff',
                            }
                        ],
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(30, 30, 30)',
                            }
                        ]
    )


    top_assists_first_table = dash_table.DataTable(
                        top_assists_data_first_col,
                        top_assists_columns,
                        style_header = {'display': 'none'},
                        style_cell={
                            'backgroundColor': '#111111',
                            'color': '#ffffff'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': ['Position', 'Parameter', 'Value']},
                                'padding-right': '10px',
                                'padding-left': '10px',
                                'text-align': 'center',
                            },
                            {
                                'if': {'column_id': 'Value'},
                                'color': '#007eff',
                            }
                        ],
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(30, 30, 30)',
                            }
                        ]
    )
    top_assists_second_table = dash_table.DataTable(
                        top_assists_data_second_col,
                        top_assists_columns,
                        style_header = {'display': 'none'},
                        style_cell={
                            'backgroundColor': '#111111',
                            'color': '#ffffff'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': ['Position', 'Parameter', 'Value']},
                                'padding-right': '10px',
                                'padding-left': '10px',
                                'text-align': 'center',
                            },
                            {
                                'if': {'column_id': 'Value'},
                                'color': '#007eff',
                            }
                        ],
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(30, 30, 30)',
                            }
                        ]
    )


    clean_sheets_first_table = dash_table.DataTable(
                        clean_sheets_data_first_col,
                        clean_sheets_columns,
                        style_header = {'display': 'none'},
                        style_cell={
                            'backgroundColor': '#111111',
                            'color': '#ffffff'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': ['Position', 'Parameter', 'Value']},
                                'padding-right': '10px',
                                'padding-left': '10px',
                                'text-align': 'center',
                            },
                            {
                                'if': {'column_id': 'Value'},
                                'color': '#007eff',
                            }
                        ],
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(30, 30, 30)',
                            }
                        ]
    )
    clean_sheets_second_table = dash_table.DataTable(
                        clean_sheets_data_second_col,
                        clean_sheets_columns,
                        style_header = {'display': 'none'},
                        style_cell={
                            'backgroundColor': '#111111',
                            'color': '#ffffff'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': ['Position', 'Parameter', 'Value']},
                                'padding-right': '10px',
                                'padding-left': '10px',
                                'text-align': 'center',
                            },
                            {
                                'if': {'column_id': 'Value'},
                                'color': '#007eff',
                            }
                        ],
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(30, 30, 30)',
                            }
                        ]
    )


    tabs_menu = dcc.Tabs(id="tabs-example-graph", value='test2', children=[
                    dcc.Tab(
                        label='League Stats', 
                        value='test2',
                        style=tab_style,
                        selected_style=tab_selected_style,
                        children=[
                            dbc.Row([
                                dbc.Col(
                                    overview_table
                                ),
                                dbc.Col(
                                    stats_table
                                )
                            ]),
                        ]),
                    dcc.Tab(
                        label='Top scorers', 
                        value='test3',
                        style=tab_style,
                        selected_style=tab_selected_style,
                        children=[
                            dbc.Row([
                                dbc.Col(
                                    top_scorers_first_table
                                ),
                                dbc.Col(
                                    top_scorers_second_table
                                )
                            ]),
                        ]),
                    dcc.Tab(
                        label='Top assists', 
                        value='test4',
                        style=tab_style,
                        selected_style=tab_selected_style,
                        children=[
                            dbc.Row([
                                dbc.Col(
                                    top_assists_first_table
                                ),
                                dbc.Col(
                                    top_assists_second_table
                                )
                            ]),
                        ]),
                    dcc.Tab(
                        label='Clean Sheets', 
                        value='test5',
                        style=tab_style,
                        selected_style=tab_selected_style,
                        children=[
                            dbc.Row([
                                dbc.Col(
                                    clean_sheets_first_table
                                ),
                                dbc.Col(
                                    clean_sheets_second_table
                                )
                            ]),
                        ]),
                ],
                style={
                        'marginTop': '30px'
                }),


    return league_logo, league_header, tabs_menu, table_title, main_table, main_table_legend




@callback(
    Input("button_id", "n_clicks"),
    background=True,
    running=[
        (Output("button_id", "disabled"), True, False),
        (Output("cancel_button_id", "disabled"), False, True),
        (
            Output("progress_bar", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        )
    ],
    cancel=[Input("cancel_button_id", "n_clicks")],
    progress=[Output("progress_bar", "value"), Output("progress_bar", "max")],
    prevent_initial_call=True
)
def update_dropdwon_seasons_list(set_progress, n_clicks):

    
    older_seasons = get_older_seasons()

    set_progress((str(1), str(len(older_seasons))))

    current_season = get_current_season_number()
    current_season_label = "Season " + str(current_season) + " (Current season)"


    all_files_keys = [0]
    all_files_value = [current_season_label]

    for i in range(0, len(older_seasons)):

        try:
            result = get_season_data(i, current_season)
            if not result:
                continue
        except:
            continue
        
        all_files_keys.append(i+1)
        all_files_value.append("Season " + older_seasons[i])


        all_files_pairs = zip(all_files_keys, all_files_value)
        all_files_dict = dict(all_files_pairs)


        # set_props("select-season-dropdown",
        #         {"options": all_files_dict}
        # )

        set_progress((str(i+2), str(len(older_seasons))))


def get_season_data(number, current_season):
        """Get data for season number from the website and save it to the file."""

        #options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        #options.add_argument('--log-level=3')
        # options.add_experimental_option(
        #     "prefs", {
        #         # block image loading
        #         "profile.managed_default_content_settings.images": 2,
        #     }
        # )
        # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")

        # driver = webdriver.Chrome(options=options)
        # wait = WebDriverWait(driver, 10)
        # driver.get(RAW_URL)
        #print(driver.current_url)

        dropdown_xpath = """//*[@id="teamSummary"]/div/div[4]/div[2]"""
        dropdown_list_xpath = """//*[@id="teamSummary"]/div/div[4]/div[2]/ul"""
        dropdown_list_option_xpath = f"""//*[@id="teamSummary"]/div/div[4]/div[2]/ul/li[{number+1}]"""
        body_xpath = """/html/body"""

        page_source = ""


        # WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath))).click()

        # WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.XPATH, dropdown_list_xpath)))

        # WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.XPATH, dropdown_list_option_xpath))).click()

        # elem = wait.until(EC.visibility_of_element_located((By.XPATH, body_xpath)))

        # page_str = elem.text

        # page_source = elem.get_attribute('outerHTML')

        # if 'current '+ current_season + ' season' in page_source:
        #     return False


        # current_filename = f"static\\stats\\season_{number+1}.html"
        # with open(current_filename , "w", encoding='utf-8') as f:
        #     f.write(page_source)

        # driver.quit()

        return True


server = app.server


if __name__ == '__main__':
    app.run_server(debug=True)