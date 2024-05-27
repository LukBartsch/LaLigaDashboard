import glob
import pathlib
import os
import requests
from typing import Tuple

import pandas as pd

from bs4 import BeautifulSoup

from common import url as URL


def set_default_season_list() -> dict:
    """Get list of all seasons available on website.

    Returns
    -------
    dict
        Dictionary with all options for dropdown menu
    """

    current_season = get_current_season_number()
    current_season_label = "Season " + str(current_season) + " (Current season)"

    all_files_keys = [0]
    all_files_value = [current_season_label]
        
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

    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    table_title = soup.find ('div', {'class':'normalContentWidth cf leagueStatsTable'}).text.strip()
    current_season = table_title[-7:]

    return current_season


def get_older_seasons() -> list:
    """Get older seasons options from website (dropdwon menu)

    Returns
    -------
    list
        List with older seasons options
    """

    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    dropdown_options = soup.find ('ul', {'class':'drop-down'}).text.strip()
    dropdown_options = dropdown_options.split('\n')

    return dropdown_options


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


def set_main_table_position_colors(len_of_legend: int, season_number: str) -> Tuple[dict, dict, dict, dict]:
    """Set colors for main table positions

    Parameters
    ----------
    len_of_legend : int
        Number of legend elements
    season_number : str
        Season number

    Returns
    -------
    Tuple[dict, dict, dict, dict]
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


def get_lists_with_top_players(top_players: BeautifulSoup, season_number: str) -> Tuple[list, list]:
    """Get list with top players

    Parameters
    ----------
    top_players : BeautifulSoup
        BeautifulSoup object with data from website 
    season_number : str
        Season number

    Returns
    -------
    Tuple[list, list]
        Two lists with info about top players names and values
    """
    top_players_name_list = []
    top_players_value_list = []

    if season_number == "Current season":
        top_players_raw_list = str(top_players.text.strip()).split('\n\n\n')

        for position in top_players_raw_list:
            splited_position = position.split('\xa0\xa0')
            top_players_name_list.append(splited_position[0])
            top_players_value_list.append(splited_position[1])
    else:
        top_players_raw_list = str(top_players.text.strip()).split('\xa0\xa0')

        for position in top_players_raw_list:
            top_players_name_list.append(position)
            top_players_value_list.append('10')

        for i in range(6):

            two_digit_stat = check_double_stat(top_players_name_list[i][:2])
            two_digit_stat_next = check_double_stat(top_players_name_list[i+1][:2])

            if two_digit_stat_next:
                if i != 0:
                    top_players_name_list[i] = top_players_name_list[i][2:]

                top_players_value_list[i] = top_players_name_list[i+1][:2]
            else:
                if i != 0 and two_digit_stat:
                    top_players_name_list[i] = top_players_name_list[i][2:]
                if i != 0 and not two_digit_stat:
                    top_players_name_list[i] = top_players_name_list[i][1:]

                top_players_value_list[i] = top_players_name_list[i+1][:1]

    return top_players_name_list[:6], top_players_value_list[:6]


def check_double_stat(stat: str) -> bool:
    """Check if stat is double digit

    Parameters
    ----------
    stat : str
        Single stat
    
    Returns
    -------
    bool
        True if stat is double digit, False if not
    """

    for digit in stat:
        if digit.isdigit():
            double_stat = True
        else:
            double_stat = False

    return double_stat


def prepare_data_about_top_players_for_datatable(name_list: list, value_list: list) -> Tuple[list, dict, dict]:
    """Prepare data about top players for datatable

    Parameters
    ----------
    name_list : list
        List with top players names
    value_list : list
        List with top players values

    Returns
    -------
    Tuple[list, dict, dict]
        Tuple with three elements:
        - list with columns names
        - dict with data for first column
        - dict with data for second column  
    """
    
    top_players_columns = [
    {"name": "Position", "id": "Position"},
    {"name": "Parameter", "id": "Parameter"},
    {"name": "Value", "id": "Value"},
    ]

    parameters=name_list[:3]
    values=value_list[:3]
    df_top_scorers = pd.DataFrame(
        dict(
            [
                ("Position", ["1.", "2.", "3."]),
                ("Parameter", parameters),
                ("Value", values),
            ]
        )
    )
    top_players_data_first_col=df_top_scorers.to_dict("records")

    parameters=name_list[3:]
    values=value_list[3:]
    df_top_scorers = pd.DataFrame(
        dict(
            [
                ("Position", ["4.", "5.", "6."]),
                ("Parameter", parameters),
                ("Value", values),
            ]
        )
    )
    top_players_data_second_col=df_top_scorers.to_dict("records")

    return top_players_columns, top_players_data_first_col, top_players_data_second_col


def get_ovierview_column(soup: BeautifulSoup) -> Tuple[list, dict]:
    """Get data for overview column

    Parameters
    ----------
    soup : BeautifulSoup
        BeautifulSoup object with data from website

    Returns
    -------
    Tuple[list, dict]
        Tuple with two elements:
        - list with columns names
        - dict with data for overview column
    """
    
    try:
        goal_match = soup.find('div', {'class':'row two-col cf ac'})
        goal_match = goal_match.text.strip().replace('\n', '')
        goal_match = goal_match.replace(' ', '')
        goal_match = goal_match.split('Goals/Match')
        goal_match_value = goal_match[0]
        goal_match_label = 'Goals / Match'
    except:
        goal_match_value = ' '
        goal_match_label = 'Goals / Match'


    try:
        first_half = soup.find('div', {'id':'beforeHalfTime'})
        second_half = soup.find('div', {'id':'afterHalfTime'})

        first_half = first_half.text.strip().split('%')
        second_half = second_half.text.strip().split('%')

        first_half_value = first_half[0] + '%'
        second_half_value = second_half[0] + '%'

        first_half_label = first_half[1] + ' (goals)'
        second_half_label = second_half[1] + ' (goals)'

    except:
        first_half_value = '50%'
        second_half_value = '50%'

        first_half_label = 'First half'
        second_half_label = 'Second half'



    overview_columns = [
        {"name": "Parameter", "id": "Parameter"},
        {"name": "Value", "id": "Value"},
    ]

    parameters=[goal_match_value, first_half_value, second_half_value]
    values=[goal_match_label, first_half_label, second_half_label]
    df_overview = pd.DataFrame(
        dict(
            [
                ("Parameter", parameters),
                ("Value", values),
            ]
        )
    )
    data_overview=df_overview.to_dict("records")

    return overview_columns, data_overview


def get_stats_column(soup: BeautifulSoup) -> Tuple[list, dict]:
    """Get data for stats column

    Parameters
    ----------
    soup : BeautifulSoup
        BeautifulSoup object with data from website

    Returns
    -------
    Tuple[list, dict]
        Tuple with two elements:
        - list with columns names
        - dict with data for stats column
    """


    try:

        stats_list = soup.find_all('h3', {'class':'sixer'})
        extra_stats_list = soup.find_all('p', {'class':'dark-gray mt01e'})
        
        min_goal = stats_list[0].text.strip()
        min_goal = min_goal.replace('min/Goal', '')
        min_goal = min_goal + ' min/goal'

        goals_in_matches = extra_stats_list[0].text.strip()
        goals_in_matches = goals_in_matches.replace('(', '')
        goals_in_matches = goals_in_matches.replace(')', '')

        clean_sheets = stats_list[2].text.strip()

        clean_sheets_in_matches = extra_stats_list[2].text.strip()
        clean_sheets_in_matches = clean_sheets_in_matches.replace('(', '')
        clean_sheets_in_matches = clean_sheets_in_matches.replace(')', '')

        both_teams_scored = stats_list[4].text.strip()

        both_teams_scored_in_matches = extra_stats_list[4].text.strip()
        both_teams_scored_in_matches = both_teams_scored_in_matches.replace('(', '')
        both_teams_scored_in_matches = both_teams_scored_in_matches.replace(')', '')

    except:
        min_goal = 'min/goal'
        goals_in_matches = 'goals in matches'
        clean_sheets = 'Clean Sheets'
        clean_sheets_in_matches = 'clean sheets in matches'
        both_teams_scored = 'Both Teams Scored'
        both_teams_scored_in_matches = 'both teams scored in matches'


    stats_columns = [
        {"name": "Parameter", "id": "Parameter"},
        {"name": "Value", "id": "Value"},
    ]
    parameters=[min_goal, clean_sheets, both_teams_scored]
    values=[goals_in_matches, clean_sheets_in_matches, both_teams_scored_in_matches]
    df_stats = pd.DataFrame(
        dict(
            [
                ("Parameter", parameters),
                ("Value", values),
            ]
        )
    )
    data_stats=df_stats.to_dict("records")

    return stats_columns, data_stats