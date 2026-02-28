import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# -----------------------------
# CONFIGURATION PAGE
# -----------------------------
st.set_page_config(
    page_title="Dashboard CoinAfrique",
    page_icon="🐾",
    layout="wide"
)

# -----------------------------
# CSS MODERNE
# -----------------------------
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #2F4F4F;
    text-align: center;
    margin-bottom: 0;
}
.sub-header {
    font-size: 1.2rem;
    color: #555;
    text-align: center;
    margin-top: 0;
}
.ranking-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 12px;
    margin: 4px 0;
    background-color: #ffffff;
    border-radius: 8px;
    border-left: 4px solid #2F4F4F;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.ranking-number {
    font-weight: bold;
    color: #2F4F4F;
}
.ranking-value {
    font-weight: 600;
    color: #1E3A3A;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# CHARGEMENT DES DONNÉES
# -----------------------------
@st.cache_data
def load_data():
    conn = sqlite3.connect("database/annoncesanimaux.db")
    df = pd.read_sql("SELECT * FROM annonces", conn)
    conn.close()

    df['prix'] = pd.to_numeric(df['prix'], errors='coerce')
    df = df.dropna(subset=['prix'])

    if 'date' not in df.columns:
        end = datetime.now()
        start = end - timedelta(days=30)
        dates = pd.date_range(start, end, periods=len(df))
        df['date'] = np.random.choice(dates, len(df))

    return df

df = load_data()

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<p class="main-header">Dashboard CoinAfrique 🐶🐑🐓</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Analyse globale des annonces par catégorie, prix et localisation</p>',
            unsafe_allow_html=True)
st.markdown("---")

# -----------------------------
# MÉTRIQUES
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📦 Total annonces", f"{len(df):,}")

with col2:
    st.metric("📊 Catégories représentées", df['categories'].nunique())

with col3:
    st.metric("💰 Prix moyen (FCFA)", f"{df['prix'].mean():,.0f}")

with col4:
    st.metric("🏙️ Adresses actives", df['adresse'].nunique())

st.markdown("---")

# -----------------------------
# DISTRIBUTION + TOP ADRESSES
# -----------------------------
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📉 Distribution des prix par catégorie")
    fig_dist = px.histogram(
        df,
        x='prix',
        nbins=40,
        color='categories',
        color_discrete_sequence=px.colors.qualitative.Set3,
        labels={'prix': 'Prix (FCFA)', 'categories': 'Catégorie'},
        marginal='box'
    )
    fig_dist.update_layout(barmode='overlay', bargap=0.05)
    st.plotly_chart(fig_dist, use_container_width=True,key="distribution_prix")

with col_right:
    st.subheader("🏆 Top adresses")
    top_villes = df['adresse'].value_counts().head(7).reset_index()
    top_villes.columns = ['Ville', 'Nombre']

    for idx, row in top_villes.iterrows():
        st.markdown(
            f"""
            <div class="ranking-item">
                <span class="ranking-number">{idx + 1}. {row['Ville']}</span>
                <span class="ranking-value">{row['Nombre']:,.0f}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

# -----------------------------
# GRAPHIQUES COMPLÉMENTAIRES
# -----------------------------
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📊 Annonces par catégorie")
    cat_counts = df['categories'].value_counts().reset_index()
    cat_counts.columns = ['Catégorie', 'Nombre']

    fig_cat = px.bar(
        cat_counts,
        x='Catégorie',
        y='Nombre',
        color='Catégorie',
        color_discrete_sequence=px.colors.qualitative.Set2,
        text='Nombre'
    )
    fig_cat.update_traces(textposition='outside')
    fig_cat.update_layout(showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig_cat, use_container_width=True,key="annonces_categorie")

with col_chart2:
    st.subheader("💰 Prix moyen par catégorie")
    prix_moy = df.groupby('categories')['prix'].mean().reset_index()
    prix_moy.columns = ['Catégorie', 'Prix moyen']

    fig_prix = px.bar(
        prix_moy,
        x='Catégorie',
        y='Prix moyen',
        color='Catégorie',
        color_discrete_sequence=px.colors.sequential.Viridis,
        text_auto='.0f'
    )
    fig_prix.update_traces(textposition='outside')
    fig_prix.update_layout(showlegend=False, xaxis_tickangle=-45)
    st.plotly_chart(fig_prix, use_container_width=True, key="prix_moyen_categorie")