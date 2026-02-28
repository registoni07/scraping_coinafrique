# **_CoinAfrique Scraper & Dashboard_**

Application de scraping et d’analyse de données des annonces d’animaux sur CoinAfrique.
Le projet permet de :

Scraper les annonces (Selenium ou BeautifulSoup)

Stocker les données dans une base SQLite

Visualiser les statistiques dans un dashboard interactif Streamlit

Télécharger les données collectées

Intégrer un formulaire d’évaluation (KoboToolbox / Google Form)

# **_Fonctionnalités_**

## **Scraping des annonces**

Scraping multi-catégories :

Chiens 🐶

Moutons 🐑

Poules / Lapins / Pigeons 🐓🐇

Autres animaux

Choix du nombre de pages à scraper

Deux méthodes disponibles :

Selenium (sites dynamiques)

BeautifulSoup (scraping classique)

## **Stockage des données**

Base de données SQLite : annoncesanimaux.db

Table principale : annonces

Colonnes :

nom

prix

adresse

image_lien

categories

## **Dashboard interactif**

Visualisation avec :

Nombre total d’annonces

Prix moyen

Top villes (adresses avec le plus d’annonces)

Répartition par catégorie

Distribution des prix

Filtres dynamiques (catégorie, prix, ville)

Technologies utilisées :

Streamlit

Pandas

Plotly

**##  Téléchargement des données**

Consultation des CSV scrapés

Téléchargement local

Export possible vers Google Colab

## **Formulaire d’évaluation**

Intégration possible d’un formulaire KoboToolbox 
directement dans l’application 
pour recueillir les avis des utilisateurs.

# **_Technologies utilisées_**

Python 3.13.9

Streamlit

Pandas

SQLite3

Selenium

BeautifulSoup

Plotly