

def get_head_row(main_table_head):

    head_row=[]

    for row in main_table_head:
        if len(row.contents)>0:
            head_row.append(row.contents[0].text.strip())
        else:
            head_row.append('')
    
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
    logos = []

    for row in main_table_body:
        cols=row.find_all('td')
        cols=[x.text.strip() for x in cols]
        body_rows.append(cols)

        logos_src = row.find_all('img')
        logos_src = logos_src[0].get('src')
        logos.append(logos_src)

    return body_rows, logos