import streamlit as st
import pandas as pd
import requests
import folium
import plotly.graph_objects as go
from streamlit_folium import folium_static

# Configuration de la page
st.set_page_config(
    page_title="Carte scolaire Occitanie",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS amélioré
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

# Dictionnaire des emojis pour les caractéristiques
CARACTERISTIQUES_EMOJI = {
    'restauration': '🍽️ Restauration',
    'hebergement': '🛏️ Internat',
    'ulis': '♿ ULIS',
    'apprentissage': '📚 Apprentissage',
    'segpa': '📖 SEGPA',
    'section_arts': '🎨 Section Arts',
    'section_cinema': '🎬 Section Cinéma',
    'section_theatre': '🎭 Section Théâtre',
    'section_sport': '⚽ Section Sport',
    'section_internationale': '🌍 Section Internationale',
    'section_europeenne': '🇪🇺 Section Européenne',
    'lycee_agricole': '🌾 Lycée Agricole',
    'lycee_militaire': '🎖️ Lycée Militaire',
    'lycee_des_metiers': '🔧 Lycée des Métiers',
    'post_bac': '🎓 Post-BAC'
}

def load_data():
    try:
        df = pd.read_csv('datasets/data_carte_scolaire_nettoye.csv')
        df['ville_recherche'] = df['com_name_upper'].astype(str) + ' (' + df['libelle_departement_eleve'].astype(str) + ')'
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {str(e)}")
        return None

def get_etablissements_api(codes_rne):
    if not codes_rne:
        return None
    
    where_clause = " OR ".join([f'identifiant_de_l_etablissement = "{code}"' for code in codes_rne])
    url = "https://data.occitanie.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-annuaire-education/records"
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

def create_map(etablissements):
    if etablissements:
        # Calculer le centre moyen de tous les établissements
        lats = [float(etab['latitude']) for etab in etablissements if 'latitude' in etab]
        lons = [float(etab['longitude']) for etab in etablissements if 'longitude' in etab]
        center = [sum(lats) / len(lats), sum(lons) / len(lons)]
        zoom_start = 11
    else:
        center = [43.6, 3.8]
        zoom_start = 12
    
    m = folium.Map(location=center, zoom_start=zoom_start)
    
    # Ajouter les marqueurs avec des couleurs différentes
    for etab in etablissements:
        if 'latitude' in etab and 'longitude' in etab:
            if etab['nom_etablissement'].startswith('Lycée'):
                icon_color = 'red'
            elif etab['nom_etablissement'].startswith('Collège'):
                icon_color = 'blue'
            else:
                icon_color = 'gray'
            
            folium.Marker(
                [etab['latitude'], etab['longitude']],
                popup=f"<strong>{etab['nom_etablissement']}</strong><br>{etab['adresse_1']}",
                tooltip=etab['nom_etablissement'],
                icon=folium.Icon(color=icon_color, icon='info-sign')
            ).add_to(m)
    
    if etablissements:
        m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=[50, 50])
    
    return m

def afficher_etablissement(etab):
    # Créer le HTML pour les badges au début
    badges_html = [f'<span class="badge">👥 <strong>Effectif :</strong> {etab["nombre_d_eleves"] if etab["nombre_d_eleves"] else "Non renseigné"}</span>']
    
    # Ajouter les badges pour les caractéristiques
    for key, emoji_label in CARACTERISTIQUES_EMOJI.items():
        if etab.get(key, "0") == "1" or etab.get(key, 0) == 1:
            badges_html.append(f'<span class="badge">{emoji_label}</span>')
    
    # Jointure de tous les badges
    badges = ''.join(badges_html)
    
    html = f"""
    <div class="result-card">
        <h3>{etab['nom_etablissement']} ({etab['type_etablissement']})</h3>
        <div class="contact-item">
            📍 {etab['adresse_1']}, {etab['code_postal']} {etab['nom_commune']}
        </div>
        <div class="contact-item">
            📞 <a href="tel:{etab['telephone']}">{etab['telephone']}</a>
        </div>
        <div class="contact-item">
            ✉️ <a href="mailto:{etab['mail']}">{etab['mail']}</a>
        </div>
        <div class="contact-item">
            🔗 <a href="{etab['web']}" target="_blank">{etab['web']}</a>
        </div>
        <div class="badge-container">
            {badges}
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def search_page():
    st.title("🏫 Recherche de l'établissement scolaire de secteur")
    
    df = load_data()
    if df is None:
        return
    
    # Ajout d'une valeur par défaut pour la ville
    villes_disponibles = ['Sélectionnez une ville'] + sorted([str(ville) for ville in df['ville_recherche'].unique()])
    ville_selectionnee = st.selectbox(
        "Rechercher une ville",
        options=villes_disponibles,
        index=0,
        key="ville_search"
    )
    
    # Ne continue que si une vraie ville est sélectionnée
    if ville_selectionnee != 'Sélectionnez une ville':
        etablissements = df[df['ville_recherche'] == ville_selectionnee]
        
        # Gestion du type d'établissement
        types_disponibles = etablissements['type_et_libelle'].dropna().unique()
        type_choisi = None
        
        if len(types_disponibles) > 1:
            types_options = ['Sélectionnez une voie'] + list(types_disponibles)
            type_choisi = st.selectbox(
                "Sélectionnez une voie",
                options=types_options,
                index=0
            )
            
            # Ne filtre que si un vrai type est sélectionné
            if type_choisi != 'Sélectionnez une voie':
                etablissements = etablissements[etablissements['type_et_libelle'] == type_choisi]
            else:
                return  # Arrête ici si aucun type n'est sélectionné
        
        # Gestion du numéro de voie
        if (etablissements['no_de_voie_debut'].notna().any() and 
            len(etablissements[['no_de_voie_debut', 'no_de_voie_fin']].drop_duplicates()) > 1):
            
            st.info("Veuillez saisir un numéro de voie")
            min_voie = int(etablissements['no_de_voie_debut'].min())
            max_voie = int(etablissements['no_de_voie_fin'].max())
            
            numero = st.number_input(
                "Numéro de voie",
                min_value=min_voie,
                max_value=max_voie,
                value=min_voie,
                step=1,
                help=f"Le numéro doit être compris entre {min_voie} et {max_voie}"
            )
            
            if numero % 2 == 0 : #numero_pair 
                    etablissements = etablissements[
                    (etablissements['no_de_voie_debut'].fillna(-1) <= numero) &
                    (etablissements['no_de_voie_fin'].fillna(float('inf')) >= numero) &
                    ((etablissements['parite']== "PI") | (etablissements['parite']== "P"))
                ]
            else :# numero_impair
                etablissements = etablissements[
                    (etablissements['no_de_voie_debut'].fillna(-1) <= numero) &
                    (etablissements['no_de_voie_fin'].fillna(float('inf')) >= numero)&
                    ((etablissements['parite']== "PI") | (etablissements['parite']== "I"))
                ]
            
        # Affichage des résultats
        if len(etablissements) > 0:
            nb_colleges = len(etablissements[etablissements['type_etablissement'] == "COLLEGE"])
            nb_lycees = len(etablissements[etablissements['type_etablissement'] == "LYCEE"])
            
            result_text = []
            if nb_colleges > 0:
                result_text.append(f"{nb_colleges} collège{'s' if nb_colleges > 1 else ''}")
            if nb_lycees > 0:
                result_text.append(f"{nb_lycees} lycée{'s' if nb_lycees > 1 else ''}")
            
            if result_text:  # N'affiche que s'il y a des résultats
                st.subheader("Résultats de la recherche")
                st.write(" et ".join(result_text) + " trouvé" + ("s" if nb_colleges + nb_lycees > 1 else ""))
                
                codes_rne = etablissements['code_rne'].tolist()
                api_data = get_etablissements_api(codes_rne)
                
                if api_data and 'results' in api_data:
                    st.subheader("Localisation des établissements")
                    map = create_map(api_data['results'])
                    folium_static(map)
                    
                    for etab in api_data['results']:
                        afficher_etablissement(etab)
        else:
            st.warning("Aucun établissement trouvé avec ces critères")
            
def about_page():
    st.title("À propos")
    st.write("""
    Cette application permet de rechercher des établissements scolaires en Occitanie.
    
    Elle utilise les données ouvertes de l'académie et permet de :
    - Rechercher par ville
    - Filtrer par type d'établissement
    - Voir la localisation sur une carte
    - Consulter les caractéristiques détaillées
    """)

def get_population_data():
    """Données de population par département (2020) SOURCE INSEE"""
    return {
        'ARIEGE': 153287,
        'AUDE': 370260,
        'AVEYRON': 279595,
        'GARD': 748437,
        'HAUTE-GARONNE': 1400039,
        'GERS': 191283,
        'HERAULT': 1175623,
        'LOT': 174208,
        'LOZERE': 76601,
        'HAUTES-PYRENEES': 229567,
        'PYRENEES-ORIENTALES': 479000,
        'TARN': 387890,
        'TARN-ET-GARONNE': 259124
    }

def stats_page():
    # Configuration du style
    st.markdown("""
        <style>
        .big-font {
            font-size:20px !important;
            color: #4F4F4F !important;
        }
        .plotly-title {
            font-size:24px !important;
            color: #4F4F4F !important;
        }
        .filter-container {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        div[data-testid="stMetricValue"] {
            color: #4F4F4F !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 style="color: #4F4F4F;">📊 Tableau de bord sur la carte scolaire des collèges et lycées publics</h1>', unsafe_allow_html=True)

    # Chargement des données
    df = load_data()
    if df is None:
        st.error("Impossible de charger les données")
        return

    # Conversion explicite des colonnes en string et nettoyage
    df['type_etablissement'] = df['type_etablissement'].fillna('').astype(str)
    df['libelle_departement_eleve'] = df['libelle_departement_eleve'].fillna('').astype(str)

    # Configuration des filtres
    with st.container():
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        col_dept, col_type = st.columns(2)

        with col_dept:
            # Filtrage des valeurs vides pour les départements
            dept_list = [d for d in df['libelle_departement_eleve'].unique() if d.strip()]
            all_departments = sorted(dept_list)
            selected_departments = st.multiselect(
                "Sélectionner un ou plusieurs départements",
                options=all_departments,
                default=all_departments,
                key="department_filter"
            )

        with col_type:
            # Filtrage des valeurs vides pour les types
            type_list = [t for t in df['type_etablissement'].unique() if t.strip()]
            all_types = ['Tous'] + sorted(type_list)
            selected_type = st.selectbox(
                "Type d'établissement",
                options=all_types,
                index=0,
                key="type_filter"
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Filtrage des données
    filtered_df = df.copy()
    if selected_departments:
        filtered_df = filtered_df[filtered_df['libelle_departement_eleve'].isin(selected_departments)]
    if selected_type != 'Tous':
        filtered_df = filtered_df[filtered_df['type_etablissement'] == selected_type]

    # Configuration des couleurs
    colors = {
        'COLLEGE': '#1f77b4',
        'LYCEE': '#ff7f0e',
        'background': '#ffffff',
        'text': '#4F4F4F'
    }

    # Métriques principales
    st.markdown('<p class="big-font">Chiffres clés</p>', unsafe_allow_html=True)
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    
    with col_stats1:
        st.metric(
            label="Total établissements",
            value=f"{len(filtered_df['code_rne'].unique()):,}"
        )
    with col_stats2:
        st.metric(
            label="Collèges",
            value=f"{len(filtered_df[filtered_df['type_etablissement'] == 'COLLEGE']['code_rne'].unique()):,}"
        )
    with col_stats3:
        st.metric(
            label="Lycées",
            value=f"{len(filtered_df[filtered_df['type_etablissement'] == 'LYCEE']['code_rne'].unique()):,}"
        )

    # Graphiques
    col1, col2 = st.columns(2)
    populations = get_population_data()

    with col1:
        # Répartition par département avec code_rne unique
        dept_count = filtered_df.groupby(['libelle_departement_eleve', 'type_etablissement'])['code_rne'].nunique().unstack(fill_value=0)
        fig_dept = go.Figure(data=[
            go.Bar(name='Collèges', x=dept_count.index, y=dept_count.get('COLLEGE', [0]*len(dept_count)), marker_color=colors['COLLEGE']),
            go.Bar(name='Lycées', x=dept_count.index, y=dept_count.get('LYCEE', [0]*len(dept_count)), marker_color=colors['LYCEE'])
        ])
        
        fig_dept.update_layout(
            title={'text': "Établissements par département", 'font': {'size': 24, 'color': colors['text']}},
            barmode='group',
            xaxis={'title': {'text': "Département", 'font': {'size': 18, 'color': colors['text']}},
                'tickfont': {'size': 14, 'color': colors['text']}, 'tickangle': 45},
            yaxis={'title': {'text': "Nombre d'établissements", 'font': {'size': 18, 'color': colors['text']}},
                'tickfont': {'size': 14, 'color': colors['text']}},
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background'],
            font={'color': colors['text']},
            height=500
        )
        st.plotly_chart(fig_dept, use_container_width=True)

    with col2:
        # Ratio établissements/population
        dept_ratio = {}
        populations = get_population_data()

        # Standardisation des noms de départements pour la correspondance
        standardized_populations = {
            name.upper(): value for name, value in populations.items()
        }

        for dept in selected_departments:
            dept_clean = dept.strip()
            dept_name = dept_clean.split(' (')[0] if ' (' in dept_clean else dept_clean
            
            if dept_name in standardized_populations:
                # Compte unique des établissements par code_rne
                count = filtered_df[filtered_df['libelle_departement_eleve'] == dept]['code_rne'].nunique()
                dept_ratio[dept_name] = (count / standardized_populations[dept_name]) * 100000

        if dept_ratio:  # Vérifie si on a des données à afficher
            fig_ratio = go.Figure(data=[
                go.Bar(
                    x=list(dept_ratio.keys()),
                    y=list(dept_ratio.values()),
                    marker_color=colors['COLLEGE'],
                    text=[f"{val:.1f}" for val in dept_ratio.values()],  # Ajoute les valeurs sur les barres
                    textposition='outside'
                )
            ])
            fig_ratio.update_layout(
                title={'text': "Établissements pour 100K habitants", 'font': {'size': 24, 'color': colors['text']}},
                xaxis={'title': {'text': "Département", 'font': {'size': 18, 'color': colors['text']}},
                    'tickfont': {'size': 14, 'color': colors['text']}, 'tickangle': 45},
                yaxis={'title': {'text': "Ratio pour 100k habitants", 'font': {'size': 18, 'color': colors['text']}},
                    'tickfont': {'size': 14, 'color': colors['text']}},
                paper_bgcolor=colors['background'],
                plot_bgcolor=colors['background'],
                font={'color': colors['text']},
                height=500,
                showlegend=False
            )
            st.plotly_chart(fig_ratio, use_container_width=True)
        else:
            st.warning("Pas de données disponibles pour le calcul du ratio")


    # Métriques sectorisation unique
    st.markdown("<p class='big-font'>Chiffres sur la sectorisation unique</p><span>La sectorisation unique signifie que toute une ville est sectorisée dans les mêmes établissements, il n'y a donc pas de granularité par adresse.</span><br>", unsafe_allow_html=True)
    col_stats12, col_stats22, col_stats32 = st.columns(3)
    
    
    with col_stats12:
        st.metric(
            label="Nombre de villes",
            value=f"{len(filtered_df['com_name_upper'].unique())}"
        )
    with col_stats22:
        villes_unique = (
            filtered_df.groupby('com_name_upper')
            .agg({'type_et_libelle': lambda x: x.isna().all()})
            ['type_et_libelle']
            .value_counts()
            .get(True, 0)
        )
        st.metric(
            label="Sectorisation collège/lycée unique",
            value=f"{villes_unique}"
        )
    with col_stats32:
        villes_unique = (
            filtered_df[filtered_df['type_etablissement']=='COLLEGE'].groupby('com_name_upper')
            .agg({'type_et_libelle': lambda x: x.isna().all()})
            ['type_et_libelle']
            .value_counts()
            .get(True, 0)
        )
        st.metric(
            label="Sectorisation collège unique",
            value=f"{villes_unique}"
        )

 
        # Préparation des données avec la liste des villes
        dept_ville_details = (
            filtered_df[filtered_df['type_et_libelle'].notnull()]
            .groupby('libelle_departement_eleve')['com_name_upper']
            .agg(list)  # Collecte toutes les villes par département
            .reset_index()
        )

    ### Graphique sectorisation unique ########################################
    # Fonction pour formater la liste des villes
    def format_ville_list(villes):
        villes_uniques = sorted(list(set(villes)))
        
        def format_line(text, max_length=50):
            if len(text) <= max_length:
                return text
            
            last_space = text[:max_length].rfind(' ')
            if last_space == -1:  # Si pas d'espace trouvé
                return text[:max_length] + "<br>" + format_line(text[max_length:])
            return text[:last_space] + "<br>" + format_line(text[last_space+1:])

        # Formater la liste des villes
        if len(villes_uniques) > 10:
            ville_list = f"Villes: {', '.join(villes_uniques[:10])}..."
        else:
            ville_list = f"Villes: {', '.join(villes_uniques)}"
        return format_line(ville_list)

    # Création du graphique avec texte personnalisé au survol
    fig_sectorisation = go.Figure(data=[
        go.Bar(
            x=dept_ville_details['libelle_departement_eleve'],
            y=[len(set(villes)) for villes in dept_ville_details['com_name_upper']],
            marker_color=colors['COLLEGE'],
            hovertemplate="<b>%{x}</b><br>" +
                        "Nombre de villes: %{y}<br>" +
                        "%{customdata}<extra></extra>",
            customdata=[format_ville_list(villes) for villes in dept_ville_details['com_name_upper']]
        )
    ])

    # Mise en page du graphique
    fig_sectorisation.update_layout(
        title={
            'text': "Nombre de villes avec sectorisations multiples par département", 
            'font': {'size': 24, 'color': colors['text']}
        },
        xaxis={
            'title': {'text': "Département", 'font': {'size': 18, 'color': colors['text']}},
            'tickfont': {'size': 14, 'color': colors['text']}, 
            'tickangle': 45
        },
        yaxis={
            'title': {'text': "Nombre de villes", 'font': {'size': 18, 'color': colors['text']}},
            'tickfont': {'size': 14, 'color': colors['text']}
        },
        paper_bgcolor=colors['background'],
        plot_bgcolor=colors['background'],
        font={'color': colors['text']},
        height=500,
        showlegend=False,
        hoverlabel=dict(
            bgcolor=colors['text'],
            font_size=14,
            font_family="Arial"
        )
    )
    st.plotly_chart(fig_sectorisation, use_container_width=True)
    st.markdown("<span>Les sectorisations multiples sont mises en place pour favoriser l'inclusion sociale.</span><br>", unsafe_allow_html=True)
    

    # Métriques données manquantes
    st.markdown("<p class='big-font'>Chiffres sur les données manquantes</p><span>", unsafe_allow_html=True)
    col_stats13, col_stats23 = st.columns(2)
    
    with col_stats13:
        villes_college = set(filtered_df[(filtered_df['type_etablissement']=='COLLEGE') & ('libelle_region' != 'HORS REGION')]['com_name_upper'].unique())
        villes_lycee = set(filtered_df[(filtered_df['type_etablissement']=='LYCEE') & ('libelle_region' != 'HORS REGION')]['com_name_upper'].unique())
        villes_college_only = villes_college - villes_lycee
        villes_lycee_only = villes_lycee - villes_college
        
        st.metric(
            label="Villes manquantes dans la carte des lycées",
            value=f"{len(villes_college_only)}"
        )
        
        st.metric(
            label="Villes manquantes dans la carte des collèges",
            value=f"{len(villes_lycee_only)}"
        )
    with col_stats23:
        adressevilles_college = set(map(tuple, 
            filtered_df[
                (filtered_df['type_etablissement']=='COLLEGE') & 
                (filtered_df['libelle_region'] != 'HORS REGION')
            ][['com_name_upper', 'type_et_libelle']].values
        ))
        adressevilles_lycee = set(map(tuple, 
            filtered_df[
                (filtered_df['type_etablissement']=='LYCEE') & 
                (filtered_df['libelle_region'] != 'HORS REGION')
            ][['com_name_upper', 'type_et_libelle']].values
        ))
        adressevilles_college_only = adressevilles_college - adressevilles_lycee - villes_lycee_only
        adressevilles_lycee_only = adressevilles_lycee - adressevilles_college - villes_college_only
        
        st.metric(
            label="Adresses manquantes dans la carte des lycées",
            value=f"{len(adressevilles_college_only)}" 
        )
        st.metric(
            label="Adresses manquantes dans la carte des collèges",
            value=f"{len(adressevilles_lycee_only)}" 
        )

def perimetre_page():
    st.title("Périmètre de recrutement d'établissement")
    st.write("À venir...")

def main():
    if st.session_state.get('page') == 'about':
        about_page()
    elif st.session_state.get('page') == 'perimetre':
        perimetre_page()
    elif st.session_state.get('page') == 'stats':
        stats_page()
    else:
        search_page()

with st.sidebar:
    st.title("☰ Menu")
    if st.button("Trouver mon établissement"):
        st.session_state['page'] = 'search'
    if st.button("Statistiques de la carte scolaire"):
        st.session_state['page'] = 'stats'
    if st.button("Périmètre de recrutement d'établissement"):
        st.session_state['page'] = 'perimetre'
    if st.button("À propos"):
        st.session_state['page'] = 'about'

if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state['page'] = 'search'
    main()