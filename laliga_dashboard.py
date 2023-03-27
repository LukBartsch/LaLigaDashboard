import requests
from bs4 import BeautifulSoup


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