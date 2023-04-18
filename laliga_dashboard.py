import requests

from dash import Dash, dash_table, html
import dash_bootstrap_components as dbc
from bs4 import BeautifulSoup
import pandas as pd

from data_manage import get_head_row, get_tooltips_row, get_body_rows


url='https://footystats-org.translate.goog/spain/la-liga?_x_tr_sl=en&_x_tr_tl=pl&_x_tr_hl=pl&_x_tr_pto=sc'
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

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




df = pd.DataFrame(body_rows, columns = head_row)
df.drop('YC', inplace=True, axis=1)
df.drop('Cor', inplace=True, axis=1)



data=df.to_dict("records")
columns = [{"name": i, "id": i} for i in df.columns]
columns[1].update({"presentation": "markdown"})


tooltip_dict = dict(zip(head_row, tooltips_head_row))

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


main_table = dash_table.DataTable(
                    data, 
                    columns,
                    tooltip_header=tooltip_dict,
                    export_headers='display',
                    fill_width=False,
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
                                'filter_query': '{Pos} >= 1 && {Pos} <= 4' ,
                                'column_id': 'Pos'
                            },
                            'backgroundColor': '#2E8B57',
                        },
                        {
                            'if': {
                                'filter_query': '{Pos} >= 5 && {Pos} <= 6' ,
                                'column_id': 'Pos'
                            },
                            'backgroundColor': '#68AA80',
                        },
                        {
                            'if': {
                                'filter_query': '{Pos} >= 18 && {Pos} <= 20' ,
                                'column_id': 'Pos'
                            },
                            'backgroundColor': '#C85F46',
                        },
                        {
                            'if': {'column_id': 'Logo'},
                            'padding-left': '16px',
                        },
                    ],
                    tooltip_delay=0,
                    tooltip_duration=None
                )

table_title = html.H2(
                    "La Liga Table (Spain) - 2022/23",
                    style={
                        'text-align': 'center',
                        'marginLeft': 'auto',
                        'marginRight': 'auto',
                        'padding': '10px',
                        'color': '#ffffff'
                    })


app.layout = dbc.Container([
                dbc.Row([
                    dbc.Col(
                        table_title     
                    ),
                    dbc.Col(
                        main_table,
                    )]
                )
            ])


if __name__ == '__main__':
    app.run_server(debug=True)