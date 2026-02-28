import requests
from bs4 import BeautifulSoup
from database.db import save_to_db
import pandas as pd
import numpy as np

def nettoyer_prix(val):
    """
    Nettoie la valeur du prix : supprime espaces, virgules, texte non numérique et convertit en float.
    Retourne np.nan si valeur invalide.
    """
    if pd.isna(val):
        return np.nan
    val = str(val).strip()
    if 'Prix sur demande' in val:
        return np.nan
    # Supprimer espaces et virgules
    val = val.replace(' ', '').replace(',', '')
    # Ne garder que les chiffres et éventuellement un point
    chiffres = ''.join(c for c in val if c.isdigit() or c == '.')
    if chiffres == '':
        return np.nan
    return float(chiffres)


def scrape_category(categorie, base_url, max_pages=1, remplir_nan=True):
    """
    Scraper une catégorie sur CoinAfrique avec BeautifulSoup
    et nettoyer automatiquement les prix.
    """
    data = []  # liste pour affichage / Streamlit

    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Page {page} inaccessible, code {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        annonces = soup.find_all("div", class_="col s6 m4 l3")  # adapte selon ton site

        for ann in annonces:
            # Titre / nom
            a_tag = ann.find("a")
            titre = a_tag['title'] if a_tag and 'title' in a_tag.attrs else "N/A"

            # Localisation
            loc_tag = ann.find("p", class_="ad__card-location")
            location = loc_tag.span.text.strip() if loc_tag and loc_tag.span else "N/A"

            # Prix
            prix_tag = ann.find("p", class_="ad__card-price")
            prix_raw = prix_tag.text.strip() if prix_tag else "N/A"
            prix = nettoyer_prix(prix_raw)

            # Image
            img_tag = ann.find("img")
            if img_tag:
                src = img_tag.get("src", "")
                if src.startswith("//"):
                    image_lien = "https:" + src
                elif src.startswith("/"):
                    image_lien = "https://sn.coinafrique.com" + src
                else:
                    image_lien = src
            else:
                image_lien = "N/A"

            # Sauvegarde dans la DB
            save_to_db(categorie, titre, prix, location, image_lien)

            # Ajouter à la liste pour affichage
            data.append({
                "Nom / Détails": titre,
                "Prix": prix,
                "Adresse": location,
                "Image": image_lien
            })

    # Transformer en DataFrame pour traitement final
    df = pd.DataFrame(data)

    # Remplir les prix manquants par la médiane si demandé
    if remplir_nan and not df.empty:
        median_prix = df['Prix'].median()
        df['Prix'] = df['Prix'].fillna(median_prix)
        # print(f"Médiane du prix pour {categorie} : {median_prix:,.0f} FCFA")

    return df.to_dict(orient="records")  # retourne la liste de dicts pour Streamlit