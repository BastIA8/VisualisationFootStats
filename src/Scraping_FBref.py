import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

players = pd.read_csv('./Data/Players2024.csv')
wanted_stats_GK = ['Goals Against', 'Shots on Target Against', 'Saves', 'Clean Sheets', 'Save% (Penalty Kicks)', 'PSxG/SoT', 'Passes Attempted (Launched)', 'Pass Completion Percentage (Launched)']
wanted_stats_Field = ['Goals', 'Assists', 'Yellow Cards', 'Red Cards', 'Shots on Target', 'Goals/Shot', 'xG: Expected Goals' 'xA: Expected Assists', 'Key Passes', 'Passes Completed', 'Pass Completion %', 'Crosses', 'Progressive Passes', 'Progressive Carries', 'Tackles Won', 'Interceptions', 'Blocks', 'Clearances', 'Errors', 'Fouls Committed', 'Fouls Drawn', 'Offsides', 'Penalty Kicks Won', 'Penalty Kicks Conceded', 'Own Goals']

def get_player_fbref_url(player_1st_name, player_last_name):

    if pd.isna(player_last_name):
        search_query = player_1st_name
    else:
        search_query = f"{player_1st_name}+{player_last_name}"

    search_url = f"https://fbref.com/en/search/search.fcgi?search={search_query}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur lors de la recherche de {player_1st_name} {player_last_name} : {response.status_code}")
        return None

    return response.url

def scrap_player_stats(player_1st_name, player_last_name, poste):
    player_url = get_player_fbref_url(player_1st_name, player_last_name)

    if not player_url:
        return None

    player_id = player_url.split("/")[-2]
    scouting_url = f"https://fbref.com/en/players/{player_id}/scout/365_m1/{player_1st_name}-{player_last_name}-Scouting-Report"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(scouting_url, headers=headers)

    if response.status_code != 200:
        print(f"Erreur lors de l'accès au scouting report de {player_1st_name} {player_last_name} : {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    player_stats = scrape_player_profile(soup, poste)
    return player_stats

def scrape_player_profile(soup, poste):
    stats = {}
    if poste == "Goalkeeper":
        table = soup.find('table', {'id': 'scout_full_GK'})
        wanted_stats = wanted_stats_GK
    elif poste == "Defence" or poste == "Left-Back" or poste == "Right-Back" or poste == "Left Midfield" or poste == "Right Midfield":
        table = soup.find('table', {'id': 'scout_full_FB'})
        wanted_stats = wanted_stats_Field
    elif poste == "Centre-Back":
        table = soup.find('table', {'id': 'scout_full_CB'})
        wanted_stats = wanted_stats_Field
    elif poste == "Attacking Midfield" or poste == "Central Midfield" or poste == "Defensive Midfield" or poste == "Midfield":
        table = soup.find('table', {'id': 'scout_full_MF'})
        wanted_stats = wanted_stats_Field
    elif poste == "Left Winger" or poste == "Right Winger":
        table = soup.find('table', {'id': 'scout_full_AM'})
        wanted_stats = wanted_stats_Field
    elif poste == "Centre-Forward" or poste == "Offence":
        table = soup.find('table', {'id': 'scout_full_FW'})
        wanted_stats = wanted_stats_Field
    #table = soup.find('table', {'id': 'scout_full_GK'})
    if table:
        rows = table.find_all('tr')
        for row in rows:
            stat_name_element = row.find('th')
            if stat_name_element:
                stat_name_text = stat_name_element.text.strip()
                if stat_name_text in wanted_stats:
                    print(f"STAT NAME {stat_name_text}")
                    stat_value_element = row.find('td', {'data-stat': 'per90'})
                    if stat_value_element:
                        stat_value = stat_value_element.text.strip()
                        print(f"STAT VALUE {stat_value}")
                        stats[stat_name_text] = stat_value
    print(f"Stats profile {stats}")
    return stats


def collect_stats(players_df):
    stats_list = []
    for index, row in players_df.iterrows():
        first_name = row['prénom']
        last_name = row['nom']
        poste = row['poste']
        print(f"Scraping des statistiques pour {first_name} {last_name}...")
        stats = scrap_player_stats(first_name, last_name, poste)
        if stats:
            stats_list.append({
                **stats
            })
        time.sleep(10)
    return stats_list

def merge_players_stats(players_df, stats_df):
    merged_df = players_df.merge(stats_df, on=['prénom', 'nom'], how='left')
    return merged_df

def clear_empty_row(df):
    pass

def save_players_data(players):
    players.to_csv("./Data/Players_stats2024.csv", index=False)

if __name__ == "__main__":
    stats = collect_stats(players)
    if stats:
        stats = pd.DataFrame(stats)
        stats_players = merge_players_stats(players, stats)
        stats_players = clear_empty_row(stats_players)
        save_players_data(stats_players)
