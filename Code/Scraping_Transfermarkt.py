import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


players = pd.read_csv('./Data/Players2024.csv')
new_stats = []


def scrap_player_stats(player_1st_name, player_last_name):
    search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={player_1st_name}+{player_last_name}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        print(f"Erreur avec {player_1st_name} {player_last_name} : {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    player_link = soup.find('a', title=f"{player_1st_name} {player_last_name}")
    print (player_link)

    if not player_link:
        print(f"Joueur non trouvé : {player_1st_name} {player_last_name}")
        return None

    player_url = f"https://www.transfermarkt.com{player_link['href']}"
    player_stats = scrape_player_profile(player_url)
    print(player_stats)
    return player_stats


def scrape_player_profile(player_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(player_url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur lors de l'accès au profil : {player_url} ({response.status_code})")
        return None
    soup = BeautifulSoup(response.content, 'html.parser')
    print(soup)
    stats = {
        'buts': extract_stat(soup, 'Goals'),
        'tirs': extract_stat(soup, 'Tirs'),
        'passes_decisives': extract_stat(soup, 'Passes décisives'),
        # Ajoute d'autres stats ici
    }
    
    return stats


def extract_stat(soup, stat_name):
    stat = soup.find('span', text=stat_name)
    if stat:
        return stat.find_next('span').text
    return None


def collect_stats(players_df):
    stats_list = []
    for index, row in players_df.iterrows():
        first_name = row['prénom']
        last_name = row['nom']
        print(f"Scraping des statistiques pour {first_name} {last_name}...")
        stats = scrap_player_stats(first_name, last_name)
        if stats:
            stats_list.append({
                'prénom': first_name,
                'nom': last_name,
                **stats
            })
        time.sleep(2)
    return stats_list


def merge_players_stats(players_df, stats_df):
    merged_df = players_df.merge(stats_df, on=['prénom', 'nom'], how='left')
    return merged_df


def save_players_data(players):
    players.to_csv("./Data/Players_stats2024.csv")


if __name__ == "__main__":
    stats = collect_stats(players)
    if stats:
        stats = pd.DataFrame(stats)
        stats_players = merge_players_stats(players,stats)
        save_players_data(stats_players)