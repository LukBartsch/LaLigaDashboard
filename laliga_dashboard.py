import requests
# import glob
# import pathlib
# import os

from dash import Dash, dash_table, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from bs4 import BeautifulSoup
import pandas as pd

from data_manage import set_files_list, get_head_row, get_tooltips_row, get_body_rows, get_zone_explanation, \
                        get_league_header, clean_list




tab_style = {
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': '#ffffff'
}

tab_selected_style = {
        'backgroundColor': '#111111',
        'borderLeft': '2px solid #007eff',
        'color': '#007eff',
}










app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])





app.layout = dbc.Container([

                dbc.Row([
                    dcc.Dropdown(
                        id = 'select-season-dropdown',
                        options = set_files_list(),
                        value = "Current season",
                        clearable = False,
                        style = {
                            'marginTop': '20px',
                        }
                    ),
                ]),
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
    Input('select-season-dropdown', 'value')
)
def update_season(value):


    if value == 'Current season':

        url='https://footystats-org.translate.goog/spain/la-liga?_x_tr_sl=en&_x_tr_tl=pl&_x_tr_hl=pl&_x_tr_pto=sc'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')


    else:

        with open("static\\stats\\" + value, encoding="utf8") as f:
            contents = f.read()

        soup = BeautifulSoup(contents, 'html.parser')



    table_title = soup.find ('div', {'class':'normalContentWidth cf leagueStatsTable'}).text.strip()

    main_table = soup.find ('table', {'class':'full-league-table table-sort col-sm-12 mobify-table'}).thead
    main_table_head = main_table.find_all ('th')


    head_row = get_head_row(main_table_head)

    # print(head_row)
    # print(len(head_row))


    tooltips_head_row = get_tooltips_row(main_table_head)

    # print(tooltips_head_row)
    # print(len(tooltips_head_row))


    main_table = soup.find ('table', {'class':'full-league-table table-sort col-sm-12 mobify-table'}).tbody
    main_table_body = main_table.find_all('tr')

    body_rows = get_body_rows(main_table_body)


    # print(body_rows[0])
    # print(len(body_rows))


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



    zone_explanation = soup.find ('ul', {'class':'zone-explanation'})
    zone_explanation_list = zone_explanation.find_all('li')

    main_table_legend = get_zone_explanation(zone_explanation_list)

    df_legend = pd.DataFrame(main_table_legend, columns=["Col", "Description"])
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


        df_league_header = pd.DataFrame(data = [league_header_first_col_list, league_header_second_col_list], columns=["1", "2", "3", "4", "5", "6"])
        df_league_header = df_league_header.transpose()
        df_league_header.columns=["1", "2"]
        league_header_data=df_league_header.to_dict("records")
        league_header_columns = [{"name": i, "id": i} for i in df_league_header.columns]

    except:
        df_league_header = pd.DataFrame()
        league_header_data=df_league_header.to_dict("records")
        league_header_columns = [{"name": i, "id": i} for i in df_league_header.columns]





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
                            {
                                'if': {
                                    'filter_query': '{#} >= 1 && {#} <= 4' ,
                                    'column_id': '#'
                                },
                                'backgroundColor': '#2E8B57',
                            },
                            {
                                'if': {
                                    'filter_query': '{#} >= 5 && {#} <= 6' ,
                                    'column_id': '#'
                                },
                                'backgroundColor': '#68AA80',
                            },
                            {
                                'if': {
                                    'filter_query': '{#} >= 18 && {#} <= 20' ,
                                    'column_id': '#'
                                },
                                'backgroundColor': '#C85F46',
                            },
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
                        style_data_conditional=[
                            {
                                'if': {
                                    'row_index': 0, 
                                    'column_id': 'Col'
                                },
                                'backgroundColor': '#2E8B57',
                            },
                            {
                                'if': {
                                    'row_index': 1, 
                                    'column_id': 'Col'
                                },
                                'backgroundColor': '#68AA80',
                            },
                            {
                                'if': {
                                    'row_index': 2, 
                                    'column_id': 'Col'
                                },
                                'backgroundColor': '#C85F46',
                            },
                        ],
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


    tabs_menu = dcc.Tabs(id="tabs-example-graph", value='test1', children=[
                    dcc.Tab(
                        label='Overview', 
                        value='test1',
                        style=tab_style,
                        selected_style=tab_selected_style),
                    dcc.Tab(
                        label='League Stats', 
                        value='test2',
                        style=tab_style,
                        selected_style=tab_selected_style),
                    dcc.Tab(
                        label='Top scorers', 
                        value='test3',
                        style=tab_style,
                        selected_style={
                                'backgroundColor': '#111111',
                                'borderLeft': '2px solid #007eff',
                                'color': '#007eff',
                        }),
                    dcc.Tab(
                        label='Top assists', 
                        value='test4',
                        style=tab_style,
                        selected_style=tab_selected_style),
                    dcc.Tab(
                        label='Clean Sheets', 
                        value='test5',
                        style=tab_style,
                        selected_style=tab_selected_style),
                ],
                style={
                        'marginTop': '30px'
                }),


    return league_logo, league_header, tabs_menu, table_title, main_table, main_table_legend



server = app.server


if __name__ == '__main__':
    app.run_server(debug=True)