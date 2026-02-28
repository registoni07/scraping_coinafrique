import streamlit as st
import pandas as pd
from database.db import create_table, clear_table
from scrapers.selenium_scraper import scrape_category_selenium
import os

# Création DB si nécessaire
os.makedirs("database", exist_ok=True)
create_table()

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/616/616408.png", width=100)
    st.title("Bienvenue !")
    st.write("Bienvenue sur l'application de scraping CoinAfrique 🐶🐑🐓")

    st.markdown("---")
    index_value = st.selectbox("Nombre de pages à scrapers", list(range(1, 101)))
    menu_option = st.selectbox(
        "Menu",
        [
            "Scraper en utilisant BeautifulSoup",
            "Scraper en utilisant Selenium",
            "Télécharger des données déjà scrapées (Web Scraper) (à venir)",
            "Voir dashboard des données",
            "Formulaire d'evaluation de l'application"
        ]
    )

# -----------------------------
# CONTENU PRINCIPAL
# -----------------------------
st.markdown(
    """
    <h1 style='text-align: center; margin-top: 50px;'>Application de scraping CoinAfrique 🐶🐑🐓</h1>
    """,
    unsafe_allow_html=True
)

# Initialiser l'état si pas défini
if "scraping" not in st.session_state:
    st.session_state.scraping = False

# -----------------------------
# SCRAPING SELON MENU
# -----------------------------
if menu_option == "Scraper en utilisant Selenium":
    st.info(f"Scraping {index_value} page(s) avec Selenium")

    if st.button("Lancer le scraping") and not st.session_state.scraping:
        st.session_state.scraping = True

        # Placeholder pour afficher le message
        status_placeholder = st.empty()
        status_placeholder.markdown("**Félicitations ! Le bouton fonctionne 👏**")

        # Réinitialiser l'état pour pouvoir recliquer
        st.session_state.scraping = False

# -----------------------------
# OPTION BEAUTIFULSOUP (inchangée)
# -----------------------------
elif menu_option == "Scraper en utilisant BeautifulSoup":
    st.info(f"Scraping {index_value} page(s) avec BeautifulSoup")

    if st.button("Lancer le scraping") and not st.session_state.scraping:
        st.session_state.scraping = True
        status_placeholder = st.empty()
        status_placeholder.markdown("**Scraping en cours, veuillez patienter ...**")

        clear_table()

        categories = {
            "Chiens": "https://sn.coinafrique.com/categorie/chiens",
            "Moutons": "https://sn.coinafrique.com/categorie/moutons",
            "Poules / Lapins / Pigeons": "https://sn.coinafrique.com/categorie/poules-lapins-et-pigeons",
            "Autres animaux": "https://sn.coinafrique.com/categorie/autres-animaux"
        }

        all_data = {}
        progress_bar = st.progress(0)

        with st.spinner("Scraping en cours, veuillez patienter ..."):
            for i, (cat, url) in enumerate(categories.items(), 1):
                from scrapers.beautifulsoup_scraper import scrape_category
                data = scrape_category(cat, url, max_pages=index_value)
                all_data[cat] = data
                progress_bar.progress(i / len(categories))

        st.success("Scraping terminé et données sauvegardées !")

        for cat, data in all_data.items():
            st.subheader(cat)
            if data:
                df = pd.DataFrame(data)
                st.caption(f"Dataset : {len(df):,} lignes x {df.shape[1]} colonnes")
                st.dataframe(df)
            else:
                st.caption("Dataset : 0 lignes x 0 colonnes")
                st.write("Aucune donnée trouvée pour cette catégorie.")

        st.session_state.scraping = False
        status_placeholder.empty()
# -----------------------------
# AFFICHER TOUS LES CSV EXISTANTS
# -----------------------------
elif menu_option == "Télécharger des données déjà scrapées (Web Scraper) (à venir)":
    # Bannière et description
    st.markdown("<h1 style='text-align: center; color: #2F4F4F;'>Données déjà scrapées 🗂️</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555;'>Vous pouvez consulter les données collectées automatiquement ou via Web Scraper par catégorie et les téléchargées.</h3>", unsafe_allow_html=True)
    st.markdown("---")

    # Mapping des fichiers vers le label que tu veux afficher
    csv_folder = "csv_data"
    csv_labels = {
        "chiens.csv": "Chiens 🐶",
        "moutons.csv": "Moutons 🐑",
        "pigeonslapins.csv": "Poules, Lapins et Pigeons 🐦🐇",
        "autres.csv": "Autres animaux 🐓🐖"
    }

    for file, label in csv_labels.items():
        csv_path = os.path.join(csv_folder, file)
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            st.subheader(label)
            st.caption(f"Dataset : {len(df):,} lignes x {df.shape[1]} colonnes")
            st.dataframe(df)
        else:
            st.warning(f"Le fichier {file} est introuvable dans {csv_folder}/")

elif menu_option == "Voir dashboard des données":
    import importlib
    import dashboard
    importlib.reload(dashboard)

elif menu_option == "Formulaire d'evaluation de l'application":

    st.markdown(
        """
        <h1 style='text-align: center; color: #2F4F4F;'>
        📝 Formulaire d’évaluation de l’application
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p style='text-align: center; font-size:18px;'>
        Merci de prendre quelques minutes pour évaluer l'application.
        </p>
        """,
        unsafe_allow_html=True
    )

    # Intégration du formulaire Kobo
    st.components.v1.iframe(
        "https://ee.kobotoolbox.org/9WG74Oku",
        height=800,
        scrolling=True
    )