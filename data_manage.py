

def get_head_row(main_table_head):

    head_row=[]

    for row in main_table_head:
        if len(row.contents)>0:
            head_row.append(row.contents[0].text.strip())
        else:
            head_row.append('')

    head_row[0]='Pos'
    head_row[1]='Logo'
    head_row[16]='YC'
    head_row[17]='Cor'

    
    return head_row



def get_tooltips_row(main_table_head):
    
    tooltips_head_row = []

    for th in main_table_head:
        span=th.find('span')
        if span:
            tooltips_head_row.append(span.text.strip())
        else:
            tooltips_head_row.append('')

    return tooltips_head_row



def get_body_rows(main_table_body):

    body_rows = []

    for row in main_table_body:
        cols=row.find_all('td')
        cols=[x.text.strip() for x in cols]
        
        logo_src = row.find_all('img')
        logo_src = logo_src[0].get('src')
        logo_markdown_url=f"[![Logo]({logo_src})](https://cdn.footystats.org)"

        cols[1]=logo_markdown_url

        body_rows.append(cols)

    return body_rows