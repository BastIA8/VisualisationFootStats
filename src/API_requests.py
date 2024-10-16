import requests
import json
import pandas as pd
import time
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')
BASE_URL = 'https://api.football-data.org/v4/'

CHAMPIONNAT_IDS = {
    'Premier League': 2021,
    'La Liga': 2014,
    'Serie A': 2019,
    'Bundesliga': 2002,
    'Ligue 1' : 2015
}


def get_teams(championship_id):
    url = f"{BASE_URL}competitions/{championship_id}/teams"
    response = api_request(url)
    if response:
        teams = response['teams']
        return teams
    return []


def get_team_players(team_id):
    url = f"{BASE_URL}teams/{team_id}"
    response = api_request(url)
    if response:
        players = response['squad']
        return players
    return []


def api_request(url):
    headers = {'X-Auth-Token': API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur {response.status_code} : {response.text}")
    except Exception as e:
        print(f"Erreur de connexion : {str(e)}")
    return None


def collect_players_from_leagues():
    start_time = time.time()
    all_players = []
    request_count = 0

    for league, league_id in CHAMPIONNAT_IDS.items():
        print(f"Récupération des équipes pour le championnat {league}...")
        teams = get_teams(league_id)
        request_count += 1
        for team in teams:
            print(f"Récupération des joueurs pour l'équipe {team['name']}...")
            players = get_team_players(team['id'])
            request_count += 1
            if players:
                for player in players:
                    player_data = {
                        'nom': player['name'],
                        'poste': player['position'],
                        'équipe': team['name'],
                        'championnat': league
                    }
                    all_players.append(player_data)
            if request_count >= 10:
                print("\nPause pour respecter la limite de requêtes.\n")
                time.sleep(60 - (time.time() - start_time) + 1)
                request_count = 0
                start_time = time.time()
    return all_players


def split_first_last_name(players):
    players[['prénom', 'nom']] = players['nom'].apply(lambda x: split_name_safe(x)).apply(pd.Series)
    cols = ['prénom', 'nom'] + [col for col in players.columns if col not in ['prénom', 'nom']]
    players = players[cols]
    return players


def split_name_safe(full_name):
    if pd.isna(full_name) or full_name.strip() == "":
        return "", ""
    parts = full_name.split(' ')
    prénom = parts[0]
    nom = ' '.join(parts[1:]) if len(parts) > 1 else ''
    return prénom, nom


def save_players_data(players):
    players.to_csv("./Data/Players2024.csv")


if __name__ == "__main__":
    players = collect_players_from_leagues()
    if players:
        players_df = pd.DataFrame(players)
        players_df = split_first_last_name(players_df)
        save_players_data(players_df)