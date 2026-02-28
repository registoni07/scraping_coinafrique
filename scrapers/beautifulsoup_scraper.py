# scrapers/beautifulsoup_scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def nettoyer_prix(val):
    """Nettoyage robuste d'une chaîne prix -> float ou np.nan"""
    if pd.isna(val):
        return np.nan
    val = str(val).strip()
    if not val or 'Prix sur demande' in val or 'Sur demande' in val:
        return np.nan
    # normaliser les espaces non-breakable
    val = val.replace('\u00A0', ' ')
    # supprimer espaces milliers et points/virgules incorrects
    # si le format utilise virgule comme décimal, il faudrait remplacer ',' -> '.'
    # ici on supprime virgules/espaces qui sont le plus souvent des séparateurs de milliers
    val = val.replace(' ', '').replace(',', '')
    # garder chiffres et éventuellement un point
    chiffres = ''.join(c for c in val if c.isdigit() or c == '.')
    if chiffres == '':
        return np.nan
    try:
        return float(chiffres)
    except:
        return np.nan

def scrape_category(categorie, base_url, max_pages=1, remplir_nan=True):
    """
    Scraper une catégorie sur CoinAfrique (BeautifulSoup) — version robuste pour Cloud.
    Retourne une liste de dicts: [{'Nom / Détails':..., 'Prix':..., 'Adresse':..., 'Image':...}, ...]
    Lève RuntimeError en cas d'erreur de requête pour permettre affichage dans Streamlit.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    data = []

    for page in range(1, max_pages + 1):
        url = f"{base_url}?page={page}"
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            # remonter l'erreur pour que l'app l'affiche
            raise RuntimeError(f"Requête vers {url} échouée: {e}")

        soup = BeautifulSoup(resp.text, "html.parser")

        # sélecteur principal (garde les deux options si site a changé)
        annonces = soup.select("div.col.s6.m4.l3")
        if not annonces:
            # fallback selectors si structure différente
            annonces = soup.select(".listing-item, .ad-card, article, .ad__card")
        # si toujours vide, on continue (on ne lève pas d'erreur pour un seul page vide)
        if not annonces:
            continue

        for ann in annonces:
            # Titre / nom
            a_tag = ann.find("a")
            titre = a_tag.get("title") if a_tag and a_tag.has_attr("title") else (a_tag.text.strip() if a_tag else "N/A")

            # Localisation
            location = "N/A"
            loc_tag = ann.select_one("p.ad__card-location span")
            if loc_tag:
                location = loc_tag.get_text(strip=True)
            else:
                # fallback
                loc_tag2 = ann.select_one(".location, .ad-location")
                if loc_tag2:
                    location = loc_tag2.get_text(strip=True)

            # Prix
            prix_raw = "N/A"
            prix_tag = ann.select_one("p.ad__card-price")
            if prix_tag:
                prix_raw = prix_tag.get_text(strip=True)
            else:
                prix_tag2 = ann.select_one(".price, .ad-price")
                if prix_tag2:
                    prix_raw = prix_tag2.get_text(strip=True)
            prix = nettoyer_prix(prix_raw)

            # Image
            image_lien = "N/A"
            img_tag = ann.find("img")
            if img_tag:
                src = img_tag.get("src") or img_tag.get("data-src") or ""
                if src.startswith("//"):
                    image_lien = "https:" + src
                elif src.startswith("/"):
                    image_lien = "https://sn.coinafrique.com" + src
                else:
                    image_lien = src

            # Ajouter à la liste
            data.append({
                "Nom / Détails": titre,
                "Prix": prix,
                "Adresse": location,
                "Image": image_lien
            })

    # DataFrame pour post-traitement (médiane)
    df = pd.DataFrame(data)
    if remplir_nan and not df.empty:
        # remplacer NaN par la médiane calculée sur les valeurs numériques
        df['Prix'] = pd.to_numeric(df['Prix'], errors='coerce')
        median_prix = df['Prix'].median()
        if not np.isnan(median_prix):
            df['Prix'] = df['Prix'].fillna(median_prix)

    # retourne la liste de dicts (compatible avec st.dataframe(pd.DataFrame(list_of_dicts)))
    return df.to_dict(orient="records")