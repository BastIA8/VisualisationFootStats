# Analyse Statistique des Joueurs de Football
Ce projet propose une exploration et une analyse approfondie des performances des joueurs de football à partir de données provenant d'API et de web scraping. L'objectif est de fournir des visualisations interactives et des comparaisons détaillées des joueurs pour mieux comprendre leurs statistiques individuelles et collectives.

## Récupération des données des équipes via API
Cette étape consiste à récupérer les informations de base des joueurs et équipes (nom, poste, championnat, etc.) des cinq grands championnats européens à l'aide de l'API Football-Data et des bibliothèques [`requests`] et [`pandas`].

## Web Scraping pour collecter les statistiques individuelles
Certaines statistiques individuelles avancées (buts, passes, interceptions, etc.) ont été récupérées à l’aide de scraping sur des plateformes comme FBref et Transfermarkt grâce à la bibliothèque python [`BeautifulSoup`].

## Visualisation et Analyse
Les données collectées ont été analysées à l’aide de bibliothèques comme [`seaborn`] et [`plotly`]. Des visualisations interactives permettent de comparer les performances des joueurs, de repérer les meilleurs talents, ou encore d’explorer des statistiques spécifiques comme les performances défensives.