import time
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from database.scraping_db import save_to_db

def nettoyer_prix(val):
    """Nettoie la valeur du prix et retourne float ou np.nan"""
    if pd.isna(val):
        return np.nan
    val = str(val).strip()
    if 'Prix sur demande' in val:
        return np.nan
    val = val.replace(' ', '').replace(',', '')
    chiffres = ''.join(c for c in val if c.isdigit() or c == '.')
    return float(chiffres) if chiffres else np.nan

def scrape_category_selenium(categorie, base_url, max_pages=1, remplir_nan=True):
    """
    Scraper une catégorie sur CoinAfrique avec Selenium (adapté pour Streamlit Cloud)
    """
    data = []

    # Configurer Chrome en mode headless pour Cloud
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")       # mode headless moderne
    options.add_argument("--no-sandbox")         # nécessaire sur conteneurs
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Installer et lancer le driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        for page in range(1, max_pages + 1):
            url = f"{base_url}?page={page}"
            driver.get(url)
            time.sleep(2)

            annonces = driver.find_elements(By.CSS_SELECTOR, "div.col.s6.m4.l3")

            for ann in annonces:
                # Titre
                try:
                    a_tag = ann.find_element(By.TAG_NAME, "a")
                    titre = a_tag.get_attribute("title") if a_tag else "N/A"
                except:
                    titre = "N/A"

                # Localisation
                try:
                    loc_tag = ann.find_element(By.CSS_SELECTOR, "p.ad__card-location span")
                    location = loc_tag.text.strip() if loc_tag else "N/A"
                except:
                    location = "N/A"

                # Prix
                try:
                    prix_tag = ann.find_element(By.CSS_SELECTOR, "p.ad__card-price")
                    prix_raw = prix_tag.text.strip() if prix_tag else "N/A"
                    prix = nettoyer_prix(prix_raw)
                except:
                    prix = np.nan

                # Image
                try:
                    img_tag = ann.find_element(By.TAG_NAME, "img")
                    src = img_tag.get_attribute("src") if img_tag else ""
                    if src.startswith("//"):
                        image_lien = "https:" + src
                    elif src.startswith("/"):
                        image_lien = "https://sn.coinafrique.com" + src
                    else:
                        image_lien = src
                except:
                    image_lien = "N/A"

                # Sauvegarde dans la DB
                save_to_db(categorie, titre, prix, location, image_lien)

                # Ajouter à la liste
                data.append({
                    "Nom / Détails": titre,
                    "Prix": prix,
                    "Adresse": location,
                    "Image": image_lien
                })

    finally:
        driver.quit()

    df = pd.DataFrame(data)

    # Remplir les NaN par la médiane si demandé
    if remplir_nan and not df.empty:
        median_prix = df['Prix'].median()
        df['Prix'] = df['Prix'].fillna(median_prix)

    return df.to_dict(orient="records")