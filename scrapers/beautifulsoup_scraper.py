import requests
from bs4 import BeautifulSoup
from database.db import save_to_db
import pandas as pd
import numpy as np
import streamlit as st  # pour afficher les erreurs sur Streamlit

def nettoyer_prix(val):
    if pd.isna(val):
        return np.nan
    val = str(val).strip()
    if 'Prix sur demande' in val:
        return np.nan
    val = val.replace(' ', '').replace(',', '')
    chiffres = ''.join(c for c in val if c.isdigit() or c == '.')
    if chiffres == '':
        return np.nan
    return float(chiffres)

def scrape_category(categorie, base_url, max_pages=1, remplir_nan=True):
    """
    Scraper une catégorie sur CoinAfrique avec BeautifulSoup
    et nettoyer automatiquement les prix.
    Affiche les erreurs et logs pour faciliter le debug sur Streamlit Cloud.
    """
    data = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/145.0.0.0 Safari/537.36"
    }

    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur sur la page {page} ({url}) : {e}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        annonces = soup.find_all("div", class_="col s6 m4 l3")

        if not annonces:
            st.warning(f"Aucune annonce trouvée sur la page {page} ({url}).")
            continue

        for ann in annonces:
            # Titre
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

            # Sauvegarde dans DB
            try:
                save_to_db(categorie, titre, prix, location, image_lien)
            except Exception as e:
                st.warning(f"Impossible de sauvegarder dans la DB : {e}")

            data.append({
                "Nom / Détails": titre,
                "Prix": prix,
                "Adresse": location,
                "Image": image_lien
            })

    df = pd.DataFrame(data)

    # Remplir les NaN par la médiane si demandé
    if remplir_nan and not df.empty:
        median_prix = df['Prix'].median()
        df['Prix'] = df['Prix'].fillna(median_prix)
        st.info(f"Médiane du prix pour {categorie} : {median_prix:,.0f} FCFA")

    if df.empty:
        st.warning(f"Aucune donnée récupérée pour la catégorie {categorie}.")

    return df.to_dict(orient="records")