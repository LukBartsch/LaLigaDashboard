import glob
import pathlib
import os
import requests

from bs4 import BeautifulSoup


def set_files_list() -> dict:
    """Get list of all files in static\stats folder

    Returns
    -------
    dict
        Dictionary with all files in static\stats folder
    """

    path = str(pathlib.Path(__file__).parent.resolve())
    files_path = path + "\static\stats"

    raw_all_files = glob.glob(files_path + "/*.txt")
    raw_all_files.sort(reverse=True)

    current_season = get_current_season_number()
    current_season_label = "Season " + str(current_season) + " (Current season)"
    

    all_files_keys = ["Current season"]
    all_files_value = [current_season_label]

    for file in raw_all_files:
        head, tail = os.path.split(file)
        all_files_keys.append(tail)

        season_number = str(tail)[-9:-4]
        splited_season_number = season_number.split("_")
        all_files_value.append("Season " + splited_season_number[0] + "/" + splited_season_number[1])
        
    all_files_pairs = zip(all_files_keys, all_files_value)
    all_files_dict = dict(all_files_pairs)

    return all_files_dict


def get_current_season_number() -> str:
    """Get current season number from website

    Returns
    -------
    str
        Current season number (string)
    """

    url='https://footystats-org.translate.goog/spain/la-liga?_x_tr_sl=en&_x_tr_tl=pl&_x_tr_hl=pl&_x_tr_pto=sc'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    table_title = soup.find ('div', {'class':'normalContentWidth cf leagueStatsTable'}).text.strip()
    table_title = table_title[-5:]

    return table_title


def get_head_row(main_table_head: BeautifulSoup) -> list:
    """Get data for table header

    Parameters
    ----------
    main_table_head : BeautifulSoup
        BeautifulSoup object with data from website 

    Returns
    -------
    list
        Clean data for table header
    """    

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


def get_tooltips_row(main_table_head: BeautifulSoup) -> list:
    """Get data for table tooltips header

    Parameters
    ----------
    main_table_head : BeautifulSoup
        BeautifulSoup object with data from website 

    Returns
    -------
    list
        Clean data for table tooltips header
    """    

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


def get_body_rows(main_table_body: BeautifulSoup) -> list:
    """Get data for table body

    Parameters
    ----------
    main_table_body : BeautifulSoup
        BeautifulSoup object with data from website 

    Returns
    -------
    list
        Clean data for table body
    """    

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


def split_last_five_games(cols: list) -> list:
    """Split and clean five last matches scores to single items

    Parameters
    ----------
    cols : list
        Raw list of last five matches scores 

    Returns
    -------
    list
        Clean list of last five last matches scores
    """    

    raw_matches_list = list(cols[11])

    matches_list = []

    if raw_matches_list != []:
        for single_match in raw_matches_list:
            if single_match != "\n":
                matches_list.append(single_match)
    else:
        matches_list = ["","","","",""]

    while len(matches_list) < 5:
        matches_list.append("")

    matches_list.reverse()

    del cols[11]

    for single_match in matches_list:
        cols.insert(11,single_match)

    return cols


def get_zone_explanation(zone_explanation_list: BeautifulSoup) -> list:
    """Get legend data for main table

    Parameters
    ----------
    zone_explanation_list : BeautifulSoup
        BeautifulSoup object with data from website 

    Returns
    -------
    list
        Clean data for table legend
    """

    zone_explanation_legend = []

    for li in zone_explanation_list:

        temp_list=[]
        if li:
            temp_list.append("")
            temp_list.append(li.text.strip())
            zone_explanation_legend.append(temp_list)

    return zone_explanation_legend


def set_legend_colors(len_of_legend: int) -> list:
    """Set colors for table legend

    Parameters
    ----------
    len_of_legend : int
        Number of legend elements

    Returns
    -------
    list
        List of colors for table legend
    """

    if len_of_legend == 3:
        legend_colors=[
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
        ]
    else:
        legend_colors=[
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
                'backgroundColor': '#629fd5',
            },
            {
                'if': {
                    'row_index': 3, 
                    'column_id': 'Col'
                },
                'backgroundColor': '#C85F46',
            },
        ]

    return legend_colors


def set_main_table_position_colors(len_of_legend: int, season_number: str) -> dict:
    """Set colors for main table positions

    Parameters
    ----------
    len_of_legend : int
        Number of legend elements
    season_number : str
        Season number

    Returns
    -------
    dict
        Four dictionarys with colors for main table positions
    """

    if len_of_legend == 3:
        champions_league_colors = {
            'if': {
                'filter_query': '{#} >= 1 && {#} <= 4' ,
                'column_id': '#'
            },
            'backgroundColor': '#2E8B57',
        }
        europa_league_colors = {
            'if': {
                'filter_query': '{#} >= 5 && {#} <= 6' ,
                'column_id': '#'
            },
            'backgroundColor': '#68AA80',
        }
        europa_league_qualifiers_colors = {}
        relegation_colors = {
            'if': {
                'filter_query': '{#} >= 18 && {#} <= 20' ,
                'column_id': '#'
            },
            'backgroundColor': '#C85F46',
        }

    elif len_of_legend == 4 and ('20_21' in season_number or '19_20' in season_number):
        champions_league_colors = {
            'if': {
                'filter_query': '{#} >= 1 && {#} <= 4' ,
                'column_id': '#'
            },
            'backgroundColor': '#2E8B57',
        }
        europa_league_colors = {
            'if': {
                'filter_query': '{#} = 5' ,
                'column_id': '#'
            },
            'backgroundColor': '#68AA80',
        }
        europa_league_qualifiers_colors = {
            'if': {
                'filter_query': '{#} = 6' ,
                'column_id': '#'
            },
            'backgroundColor': '#629fd5',
        }
        relegation_colors = {
            'if': {
                'filter_query': '{#} >= 18 && {#} <= 20' ,
                'column_id': '#'
            },
            'backgroundColor': '#C85F46',
        }
    else:
        champions_league_colors = {
            'if': {
                'filter_query': '{#} >= 1 && {#} <= 3' ,
                'column_id': '#'
            },
            'backgroundColor': '#2E8B57',
        }
        europa_league_colors = {
            'if': {
                'filter_query': '{#} = 4' ,
                'column_id': '#'
            },
            'backgroundColor': '#68AA80',
        }
        europa_league_qualifiers_colors = {
            'if': {
                'filter_query': '{#} >= 5 && {#} <= 6' ,
                'column_id': '#'
            },
            'backgroundColor': '#629fd5',
        }
        relegation_colors = {
            'if': {
                'filter_query': '{#} >= 18 && {#} <= 20' ,
                'column_id': '#'
            },
            'backgroundColor': '#C85F46',
        }

    return champions_league_colors, europa_league_colors, europa_league_qualifiers_colors, relegation_colors



def get_league_header(league_header_divs: BeautifulSoup) -> list:
    """Get data for league header

    Parameters
    ----------
    league_header_divs : BeautifulSoup
        BeautifulSoup object with data from website 

    Returns
    -------
    list
        Clean data for league header
    """

    league_header_list = []

    for div in league_header_divs:
        league_header_list.append(div.text.strip())
    
    return league_header_list


def clean_list(first_col: list, second_col: list) -> list:
    """Clean data for league header and remove duplicate elements

    Parameters
    ----------
    first_col : list
        League header - first column
    second_col : list
        League header - second column

    Returns
    -------
    list
        Clean second column for league header
    """

    cleaned_list = []

    for single_word in second_col:
        if not single_word in first_col and single_word:
            splited_word = single_word.split(" ", 1)[0]
            cleaned_list.append(splited_word)

    return cleaned_list