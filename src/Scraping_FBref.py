import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import glob
from unidecode import unidecode

wanted_stats_GK = ['Goals Against', 'Shots on Target Against', 'Saves', 'Clean Sheets', 'Save% (Penalty Kicks)', 'PSxG/SoT', 'Passes Attempted (Launched)', 'Pass Completion Percentage (Launched)']
wanted_stats_Field = ['Goals', 'Assists', 'Yellow Cards', 'Red Cards', 'Shots on Target', 'Goals/Shot', 'xG: Expected Goals' 'xA: Expected Assists', 'Key Passes', 'Passes Completed', 'Pass Completion %', 'Crosses', 'Progressive Passes', 'Progressive Carries', 'Tackles Won', 'Interceptions', 'Blocks', 'Clearances', 'Errors', 'Fouls Committed', 'Fouls Drawn', 'Offsides', 'Penalty Kicks Won', 'Penalty Kicks Conceded', 'Own Goals']

def get_player_fbref_url(player_1st_name, player_last_name=None):
    search_query = player_1st_name
    if not pd.isna(player_last_name):
        search_query += f"+{player_last_name}"

    search_url = f"https://fbref.com/en/search/search.fcgi?search={search_query}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur lors de la recherche de {player_1st_name} {player_last_name} : {response.status_code}")
        return None

    return response.url

def get_player_match_count(soup):
    match_section = soup.find('div', {'class': 'p1'})
    
    if match_section:
        match_block = match_section.find('div', recursive=False)
        if match_block:
            label = match_block.find('span', {'class': 'poptip', 'data-tip': 'Matches Played by the player or squad'})
            if label:
                match_values = [int(p.get_text(strip=True)) for p in match_block.find_all('p') if p.get_text(strip=True).isdigit()]
                if match_values:
                    total_matches = sum(match_values)
                    return total_matches
    return 0

def scrap_player_stats(player_1st_name, player_last_name, poste):
    player_url = get_player_fbref_url(player_1st_name, player_last_name)

    if not player_url:
        return None

    player_id = player_url.split("/")[-2]
    scouting_url = f"https://fbref.com/en/players/{player_id}/scout/365_m1/{player_1st_name}"

    if not pd.isna(player_last_name):
        scouting_url += f"-{player_last_name}"
    scouting_url += "-Scouting-Report"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(scouting_url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur lors de l'accès au scouting report de {player_1st_name} {player_last_name} : {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    match_count = get_player_match_count(soup)
    player_stats = {'match_played': match_count}
    player_stats.update(scrape_player_profile(soup, poste))
    return player_stats

def scrape_player_profile(soup, poste):
    stats = {}
    table_id = {
        "Goalkeeper": 'scout_full_GK',
        "Defence": 'scout_full_FB',
        "Right-Back": 'scout_full_FB',
        "Left-Back": 'scout_full_FB',
        "Right Midfield": 'scout_full_FB',
        "Left Midfield": 'scout_full_FB',
        "Centre-Back": 'scout_full_CB',
        "Midfield": 'scout_full_MF',
        "Defensive Midfield": 'scout_full_MF',
        "Attacking Midfield": 'scout_full_MF',
        "Central Midfield": 'scout_full_MF',
        "Right Winger": 'scout_full_AM',
        "Left Winger": 'scout_full_AM',
        "Centre-Forward": 'scout_full_FW',
        "Offense": 'scout_full_FW'
    }.get(poste, 'scout_full_FW')
    wanted_stats = wanted_stats_GK if poste == "Goalkeeper" else wanted_stats_Field

    table = soup.find('table', {'id': table_id})
    
    if table:
        rows = table.find_all('tr')
        for row in rows:
            stat_name_element = row.find('th')
            if stat_name_element:
                stat_name_text = stat_name_element.text.strip()
                if stat_name_text in wanted_stats:
                    stat_value_element = row.find('td', {'data-stat': 'per90'})
                    if stat_value_element:
                        stat_value = stat_value_element.text.strip()
                        stats[stat_name_text] = stat_value
    return stats

def collect_stats(players_df, checkpoint_interval=100):
    stats_list = []
    for index, row in players_df.iterrows():
        first_name = row['prénom']
        last_name = row['nom']
        poste = row['poste']
        print(f"Scraping des statistiques pour {first_name} {last_name}...")
        stats = scrap_player_stats(first_name, last_name, poste)

        if stats:
            stats_list.append({
                'prénom': first_name,
                'nom': last_name,
                **stats
            })
        
        if (index + 1) % checkpoint_interval == 0:
            pd.DataFrame(stats_list).to_csv(f"./Data/checkpoint_{index + 1}.csv", index=False)
            print(f"Checkpoint sauvegardé pour {index + 1} joueurs.")

        time.sleep(15)
    return stats_list

def merge_players_stats(players_df, stats_df):
    merged_df = players_df.merge(stats_df, on=['prénom', 'nom'], how='left')
    return merged_df

def clear_empty_row(df, max_missing_cols=25):
    df['missing_count'] = df.isnull().sum(axis=1)
    df_cleaned = df[df['missing_count'] <= max_missing_cols].drop(columns=['missing_count'])
    
    return df_cleaned
    
def save_players_data(players):
    players.to_csv("./Data/Players_stats2024.csv", index=False)

if __name__ == "__main__":
    players = pd.read_csv('./Data/Players2024.csv')

    try:
        checkpoint_files = sorted(glob.glob("./Data/checkpoint_*.csv"))
        if checkpoint_files:
            last_checkpoint = checkpoint_files[-1]
            processed_stats = pd.read_csv(last_checkpoint)
            starting_index = len(processed_stats)
            print(f"Reprise à partir de {starting_index} joueurs.")
        else:
            processed_stats = pd.DataFrame()
            starting_index = 0
    except Exception as e:
        print("Erreur lors du chargement du checkpoint:", e)
        processed_stats = pd.DataFrame()
        starting_index = 0

    new_stats = collect_stats(players[starting_index:])
    if new_stats:
        new_stats = pd.DataFrame(new_stats)
        stats_players = pd.concat([processed_stats, new_stats], ignore_index=True)
        stats_players = clear_empty_row(stats_players)
        save_players_data(stats_players)