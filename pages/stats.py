import streamlit as st
import plotly.graph_objects as go

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
                "Sélectionnez le type d'établissement",
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

    # Fonction pour regrouper par département
    @st.cache_data
    def group_by_dept(data_set):
        dept_counts = {}
        for item in data_set:
            ville = item[0] if isinstance(item, tuple) else item
            dept = filtered_df[filtered_df['com_name_upper'] == ville]['libelle_departement_eleve'].iloc[0]
            dept_counts[dept] = dept_counts.get(dept, 0) + 1
        return dept_counts

    villes_missing_lycees = group_by_dept(villes_college_only)
    villes_missing_colleges = group_by_dept(villes_lycee_only)
    addr_missing_lycees = group_by_dept(adressevilles_college_only)
    addr_missing_colleges = group_by_dept(adressevilles_lycee_only)

    # Création des 4 graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique 1: Villes manquantes dans la carte des lycées
        fig1 = go.Figure(data=[
            go.Bar(
                x=list(villes_missing_lycees.keys()),
                y=list(villes_missing_lycees.values()),
                marker_color='#1f77b4',
                hovertemplate="<b>%{x}</b><br>" +
                             "Nombre de villes: %{y}<br>" +
                             "%{customdata}<extra></extra>",
                customdata=[format_ville_list([v for v in villes_college_only 
                           if filtered_df[filtered_df['com_name_upper'] == v]['libelle_departement_eleve'].iloc[0] == dept])
                           for dept in villes_missing_lycees.keys()]
            )
        ])
        fig1.update_layout(
            title={
            'text': "Villes manquantes dans la carte des lycées", 
            'font': {'size': 18, 'color': colors['text']}
            },
            xaxis={
                'title': {'text': "Département", 'font': {'size': 18, 'color': colors['text']}},
                'tickfont': {'size': 12, 'color': colors['text']}, 
                'tickangle': 45
            },
            yaxis={
                'title': {'text': "Nombre de villes", 'font': {'size': 18, 'color': colors['text']}},
                'tickfont': {'size': 12, 'color': colors['text']}
            },
            height=400,
            showlegend=False,
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background'],
            font={'color': colors['text']},
            hoverlabel=dict(
                bgcolor=colors['text'],
                font_size=14,
                font_family="Arial"
            )
        )
        
        st.plotly_chart(fig1, use_container_width=True)

        # Graphique 3: Villes manquantes dans la carte des collèges
        fig3 = go.Figure(data=[
            go.Bar(
                x=list(villes_missing_colleges.keys()),
                y=list(villes_missing_colleges.values()),
                marker_color='#2ca02c',
                hovertemplate="<b>%{x}</b><br>" +
                             "Nombre de villes: %{y}<br>" +
                             "%{customdata}<extra></extra>",
                customdata=[format_ville_list([v for v in villes_lycee_only 
                           if filtered_df[filtered_df['com_name_upper'] == v]['libelle_departement_eleve'].iloc[0] == dept])
                           for dept in villes_missing_colleges.keys()]
            )
        ])
        fig3.update_layout(
            title={
            'text': "Villes manquantes dans la carte des collèges", 
            'font': {'size': 18, 'color': colors['text']}
            },
            xaxis={
                'title': {'text': "Département", 'font': {'size': 18, 'color': colors['text']}},
                'tickfont': {'size': 12, 'color': colors['text']}, 
                'tickangle': 45
            },
            yaxis={
                'title': {'text': "Nombre de villes", 'font': {'size': 18, 'color': colors['text']}},
                'tickfont': {'size': 12, 'color': colors['text']}
            },
            height=400,
            showlegend=False,
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background'],
            font={'color': colors['text']},
            hoverlabel=dict(
                bgcolor=colors['text'],
                font_size=14,
                font_family="Arial"
            )
        )
        st.plotly_chart(fig3, use_container_width=True)


    with col2:
        # Graphique 2: Adresses manquantes dans la carte des lycées
        fig2 = go.Figure(data=[
            go.Bar(
                x=list(addr_missing_lycees.keys()),
                y=list(addr_missing_lycees.values()),
                marker_color='#ff7f0e',
                hovertemplate="<b>%{x}</b><br>" +
                             "Nombre d'adresses: %{y}<br>" +
                             "%{customdata}<extra></extra>",
                customdata=[format_ville_list([v[0] for v in adressevilles_college_only 
                           if filtered_df[filtered_df['com_name_upper'] == v[0]]['libelle_departement_eleve'].iloc[0] == dept])
                           for dept in addr_missing_lycees.keys()]
            )
        ])
        fig2.update_layout(
            title={
            'text': "Adresses manquantes dans la carte des lycées", 
            'font': {'size': 18, 'color': colors['text']}
            },
            xaxis={
                'title': {'text': "Département", 'font': {'size': 18, 'color': colors['text']}},
                'tickfont': {'size': 12, 'color': colors['text']}, 
                'tickangle': 45
            },
            yaxis={
                'title': {'text': "Nombre d'adresses", 'font': {'size': 18, 'color': colors['text']}},
                'tickfont': {'size': 12, 'color': colors['text']}
            },
            height=400,
            showlegend=False,
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background'],
            font={'color': colors['text']},
            hoverlabel=dict(
                bgcolor=colors['text'],
                font_size=14,
                font_family="Arial"
            )
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Graphique 4: Adresses manquantes dans la carte des collèges
        fig4 = go.Figure(data=[
            go.Bar(
                x=list(addr_missing_colleges.keys()),
                y=list(addr_missing_colleges.values()),
                marker_color='#d62728',
                hovertemplate="<b>%{x}</b><br>" +
                             "Nombre d'adresses: %{y}<br>" +
                             "%{customdata}<extra></extra>",
                customdata=[format_ville_list([v[0] for v in adressevilles_lycee_only 
                           if filtered_df[filtered_df['com_name_upper'] == v[0]]['libelle_departement_eleve'].iloc[0] == dept])
                           for dept in addr_missing_colleges.keys()]
            )
        ])
        fig4.update_layout(
            title={
                'text': "Adresses manquantes dans la carte des collèges", 
                'font': {'size': 18, 'color': colors['text']}
            },
            xaxis={
                'title': {'text': "Département", 'font': {'size': 18, 'color': colors['text']}},
                'tickfont': {'size': 12, 'color': colors['text']}, 
                'tickangle': 45
            },
            yaxis={
                'title': {'text': "Nombre d'adresses", 'font': {'size': 18, 'color': colors['text']}},
                'tickfont': {'size': 12, 'color': colors['text']}
            },
            height=400,
            showlegend=False,
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background'],
            font={'color': colors['text']},
            hoverlabel=dict(
                bgcolor=colors['text'],
                font_size=14,
                font_family="Arial"
            )
        )
        st.plotly_chart(fig4, use_container_width=True)
