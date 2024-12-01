import streamlit as st
import requests
import folium
from streamlit_folium import folium_static

from main import load_data, get_etablissements_api

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

def get_etablissements_api(codes_rne):
    """Récupère les informations détaillées des établissements via l'API"""
    retour = []
    for code in codes_rne:
        try:
            url = f"https://data.occitanie.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-annuaire-education/records"
            params = {
                "limit": 20,
                "refine": f"identifiant_de_l_etablissement:{code}"
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data["results"]:  # Vérifier si des résultats existent
                retour.extend(data["results"])  # Ajouter directement le résultat sans le wrapper dans une liste
        except Exception as e:
            st.error(f"Erreur lors de la récupération des données pour {code}: {str(e)}")
            continue
    
    return {
        "total_count": len(retour),
        "results": retour
    }  

def get_coordinates(code_insee, type_et_libelle, com_name_upper):
    """
    Récupère les coordonnées à partir des informations de l'adresse
    
    Args:
        code_insee (str): Code INSEE de la commune
        type_et_libelle (str): Libellé de la voie
        com_name_upper (str): Nom de la commune en majuscules
    
    Returns:
        tuple: (longitude, latitude) ou None si non trouvé
    """
    try:
        # Construction de l'URL en fonction de la présence de type_et_libelle
        base_url = "https://api-adresse.data.gouv.fr/search/"
        
        if type_et_libelle:
            params = {
                'q': type_et_libelle,
                'type': 'street',
                'citycode': int(code_insee)
            }
        else:
            params = {
                'q': com_name_upper
            }
        
        # Appel à l'API
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Vérification et extraction des coordonnées
        if data.get('features') and len(data['features']) > 0:
            coordinates = data['features'][0]['geometry']['coordinates']
            return [coordinates[1], coordinates[0]]
        
        return None
        
    except Exception as e:
        print(f"Erreur lors de la géolocalisation : {str(e)}")
        return None

def create_map(etablissements, code_insee, type_et_libelle, com_name_upper):
    coord_ville = get_coordinates(code_insee, type_et_libelle, com_name_upper)
    lats, lons = [], []
    if coord_ville != None:
        lats += [float(coord_ville[0])]
        lons += [float(coord_ville[1])]
    if etablissements:
        # Calculer le centre moyen de tous les établissements
        lats += [float(etab['latitude']) for etab in etablissements if 'latitude' in etab]
        lons += [float(etab['longitude']) for etab in etablissements if 'longitude' in etab]
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
    if coord_ville != None:
        if type_et_libelle != None:
            survol = type_et_libelle
        else:
            survol = com_name_upper
            type_et_libelle = ""
        folium.Marker(
            coord_ville,
            popup=f"<strong>{com_name_upper}</strong><br>{type_et_libelle}",
            tooltip=survol,
            icon=folium.Icon(color='green', icon='home')
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
    st.title("🏫 Recherchez de l'établissement scolaire de votre secteur")
    
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
                    map = create_map(api_data['results'], etablissements['code_insee'].tolist()[0], type_choisi, ville_selectionnee)
                    print(etablissements['code_insee'].tolist()[0], type_choisi, ville_selectionnee)
                    folium_static(map)
                    
                    for etab in api_data['results']:
                        afficher_etablissement(etab)
        else:
            st.warning("Aucun établissement trouvé avec ces critères")