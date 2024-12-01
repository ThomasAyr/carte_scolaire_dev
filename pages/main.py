import streamlit as st
import pandas as pd
import requests
import folium
import plotly.graph_objects as go
from streamlit_folium import folium_static

from pages.search import search_page, get_etablissements_api, get_coordinates, create_map, afficher_etablissement
from pages.stats import stats_page, get_population_data
from pages.about import about_page
from pages.legal import legal_page
from pages.perimetre import perimetre_page

# Configuration de la page
st.set_page_config(
    page_title="Carte scolaire Occitanie",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Carte Scolaire Occitanie",
        'Get Help': 'https://github.com/ThomasAyr/carte_scolaire_dev',
    }
)

with st.sidebar:
    st.image("graphics composents/school-map-logo-text.svg", width=250)
    st.markdown("---")

# Style CSS
st.markdown("""
    <style>    
    /* Style gris */
    p, h1, h2, h3, ul, li .contact-item, .etablissement-info, .main h1, .main h2, .main h3, .main h4, .main p, .main label, .main div {
        color: #4F4F4F !important;
    }
            
    button div p {
            color: white !important;
    }

    /* Style des cartes établissements */
    .result-card {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        border: 1px solid #e0e0e0;
    }
    
    /* Style des badges caractéristiques */
    .badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 1rem;
        justify-content: flex-start;
    }
    
    .badge {
        color: #4F4F4F;
        flex: 0 0 auto;
        background-color: #f8f9fa;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        border: 1px solid #dee2e6;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        white-space: nowrap;
    }
    
    .badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        background-color: #e9ecef;
    }
    
    /* Style des informations de contact */
    .contact-info {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 1rem 0;
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
    }
    
    .contact-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
    }
    
    .contact-item a {
        color: #0066cc;
        text-decoration: none;
    }
    
    .contact-item a:hover {
        text-decoration: underline;
        color: #004494;
    }
    
    /* Style des infos établissement */
    .etablissement-info {
        margin-top: 1rem;
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
    }

    /* Ajustements supplémentaires */
    .stApp {
        background-color: white;
        color: #4F4F4F !important;
    }

    .stSidebar {
        background-color: #262730;
    }

    .stSelectbox {
        color: white !important;
    }
    
    /* Style pour les messages d'info et warning */
    .stAlert > div {
        color: #4F4F4F !important;
    }
    </style>
""", unsafe_allow_html=True)

def load_data():
    try:
        df = pd.read_csv('datasets/data_carte_scolaire_nettoye.csv')
        df['ville_recherche'] = df['com_name_upper'].astype(str) + ' (' + df['libelle_departement_eleve'].astype(str) + ')'
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {str(e)}")
        return None

def get_etablissements_api(codes_rne):
    """Récupère les informations détaillées des établissements via l'API"""
    """À un quota très restent de requêtes, il est préférable de ne pas utiliser cette fonction et d'utiliser la suivante"""
    if not codes_rne:
        return None
    
    where_clause = " OR ".join([f'identifiant_de_l_etablissement = "{code}"' for code in codes_rne])
    url = "https://data.occitanie.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-annuaire-education/api"
    params = {
        "where": where_clause,
        "limit": 20
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {str(e)}")
        return None

def main():
    if st.session_state.get('page') == 'about':
        about_page()
    elif st.session_state.get('page') == 'perimetre':
        perimetre_page()
    elif st.session_state.get('page') == 'stats':
        stats_page()
    elif st.session_state.get('page') == 'legal':
        legal_page()
    else:
        search_page()

with st.sidebar:
    if st.button("Trouver mon établissement de secteur"):
        st.session_state['page'] = 'search'
    if st.button("Périmètre de recrutement d'établissement"):
        st.session_state['page'] = 'perimetre'
    if st.button("Statistiques sur la carte scolaire"):
        st.session_state['page'] = 'stats'
    if st.button("À propos"):
        st.session_state['page'] = 'about'
    if st.button("Mentions légales"):
        st.session_state['page'] = 'legal'

if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state['page'] = 'search'
    main()