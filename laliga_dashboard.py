import requests

from dash import Dash, dash_table
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



data=df.to_dict("records")
columns = [{"name": i, "id": i} for i in df.columns]
columns[1].update({"presentation": "markdown"})


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


main_table = dash_table.DataTable(
                    data, 
                    columns,
                    row_deletable=True,
                    export_headers='display',
                    fill_width=False,
                    style_cell={
                        'padding-right': '10px',
                        'padding-left': '10px',
                        'text-align': 'center',
                        'marginLeft': 'auto',
                        'marginRight': 'auto'
                    },
                )


app.layout = dbc.Container([
                dbc.Row([
                    dbc.Col(
                        main_table,
                    )]
                )
            ])


if __name__ == '__main__':
    app.run_server(debug=True)