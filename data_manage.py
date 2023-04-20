

def get_head_row(main_table_head):

    head_row=[]

    for row in main_table_head:
        if len(row.contents)>0:
            if row.contents[0].text.strip() == "Last 5":
                for i in range(5):
                    head_row.append(str(i+1))
            else:
                head_row.append(row.contents[0].text.strip())
        else:
            head_row.append('')

    head_row[0]='#'
    head_row[1]='Logo'
    head_row[20]='YC'
    head_row[21]='Cor'

    
    return head_row



def get_tooltips_row(main_table_head):
    
    tooltips_head_row = []

    for th in main_table_head:
        span=th.find('span')
        if span:
            tooltips_head_row.append(span.text.strip())

        else:
            tooltips_head_row.append('')

    for i in range(5):
        tooltips_head_row.insert(11+i, str(i+1))

    tooltips_head_row[16]='Points Per Game'
    del tooltips_head_row[17]

    return tooltips_head_row



def get_body_rows(main_table_body):

    body_rows = []

    for row in main_table_body:
        cols=row.find_all('td')
        cols=[x.text.strip() for x in cols]

        cols = split_last_five_games(cols)
        
        logo_src = row.find_all('img')
        logo_src = logo_src[0].get('src')
        logo_markdown_url=f"[![Logo]({logo_src}#thumbnail)](https://cdn.footystats.org)"

        cols[1]=logo_markdown_url

        body_rows.append(cols)

    return body_rows


def split_last_five_games(cols):

    raw_matches_list = list(cols[11])
    matches_list = []
    for single_match in raw_matches_list:
        if single_match != "\n":
            matches_list.append(single_match)

    matches_list.reverse()

    del cols[11]

    for single_match in matches_list:
        cols.insert(11,single_match)

    return cols

def get_zone_explanation(zone_explanation_list):

    zone_explanation_legend = []

    for li in zone_explanation_list:

        temp_list=[]
        if li:
            temp_list.append("")
            temp_list.append(li.text.strip())
            zone_explanation_legend.append(temp_list)

    return zone_explanation_legend