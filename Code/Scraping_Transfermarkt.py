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

    if not player_link:
        print(f"Joueur non trouvé : {player_1st_name} {player_last_name}")
        return None

    player_url = f"https://www.transfermarkt.com{player_link['href']}"
    player_stats = scrape_player_profile(player_url)
    print(f"Stats : {player_stats}")
    return player_stats


def scrape_player_profile(player_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(player_url, headers=headers)

    if response.status_code != 200:
        print(f"Erreur lors de l'accès au profil : {player_url} ({response.status_code})")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    stats = {
        'buts': extract_stat(soup, 'Goals'),
        'tirs': extract_stat(soup, 'Tirs'),
        'passes_decisives': extract_stat(soup, 'Passes décisives'),
        # Ajoute d'autres stats ici
    }
    return stats


def extract_stat(soup, stat_name):
    # Trouve l'élément <span> ou autre contenant le nom de la statistique (par ex. 'Goals')
    stat_item = soup.find('span', string=stat_name)
    print(f"STATS {stat_item}")

    if stat_item:
        # Remonte à l'élément parent puis trouve la valeur correspondante dans l'élément <a>
        stat_container = stat_item.find_parent('li', class_='tm-player-performance__stats-list-item svelte-1byxyai')
        print(stat_container)
        if stat_container:
            stat_value = stat_container.find('a', class_='tm-player-performance__stats-list-item-value svelte-1byxyai')
            print(stat_value)
            if stat_value:
                return stat_value.text.strip()  # Récupère la valeur (le nombre de buts par exemple)
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