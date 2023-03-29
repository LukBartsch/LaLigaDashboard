import requests

from bs4 import BeautifulSoup
import pandas as pd


url='https://footystats-org.translate.goog/spain/la-liga?_x_tr_sl=en&_x_tr_tl=pl&_x_tr_hl=pl&_x_tr_pto=sc'
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')
print(soup.title)

# print(soup.table)
main_table = soup.find ('table', {'class':'full-league-table table-sort col-sm-12 mobify-table'}).thead
main_table_head = main_table.find_all ('th')

head_row=[]

for row in main_table_head:
    if len(row.contents)>0:
        head_row.append(row.contents[0].text.strip())
    else:
        head_row.append('')

print(head_row)


body_row=[]
logos = []

main_table = soup.find ('table', {'class':'full-league-table table-sort col-sm-12 mobify-table'}).tbody
main_table_body = main_table.find_all('tr')

for row in main_table_body:
    cols=row.find_all('td')
    cols=[x.text.strip() for x in cols]
    # print(cols)
    # print(len(cols))
    body_row.append(cols)

    logos_src = row.find_all('img')
    logos_src = logos_src[0].get('src')
    logos.append(logos_src)


for team in body_row:
    print(team)

# print(logos)

df = pd.DataFrame(body_row, columns = head_row)

print(df)

data=df.to_dict("records")
columns = [{"name": i, "id": i} for i in df.columns]