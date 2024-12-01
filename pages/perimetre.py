import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import folium_static
from io import StringIO

def load_data_annuaire():
    try:
        df = pd.read_csv('datasets/fr-en-annuaire-education.csv', sep=';')
        df = df[(df['Type_etablissement'].isin(['Lycée', 'Collège'])) 
                & (df['Statut_public_prive'] == 'Public') 
                & (df['etat'] == 'OUVERT')]
        df = df[~df['Nom_etablissement'].str.contains('professionnel', case=False)]
        df = df[~df['Nom_etablissement'].str.contains('Cité scolaire', case=False)]
        df['etab_recherche'] = df['Nom_etablissement'].astype(str) + ' (' + df['Nom_commune'].astype(str) + ')'
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {str(e)}")
        return None

def create_address_map(results, etablissement_data):
    """
    Creates a map with all the addresses (in gray) and the establishment (in red).
    
    Args:
        results (pd.DataFrame): DataFrame with the geocoding results (x, y).
        etablissement_data (pd.DataFrame): DataFrame with the data for the establishment, including latitude and longitude.
    """
    # Get all valid latitude and longitude values from the results
    lats = [float(row['latitude']) for _, row in results.iterrows() if pd.notna(row['latitude'])]
    lons = [float(row['longitude']) for _, row in results.iterrows() if pd.notna(row['longitude'])]
    
    if not etablissement_data.empty:
        lats.append(float(etablissement_data['latitude'].iloc[0]))
        lons.append(float(etablissement_data['longitude'].iloc[0]))

    if lats and lons:
        center = [sum(lats) / len(lats), sum(lons) / len(lons)]
        zoom_start = 11
    else:
        center = [43.6, 3.8]  # Default center
        zoom_start = 12

    # Create the map
    m = folium.Map(location=center, zoom_start=zoom_start)
    
    # Add a marker for the establishment in red, if provided
    if not etablissement_data.empty:
        folium.Marker(
            [float(etablissement_data['latitude'].iloc[0]), float(etablissement_data['longitude'].iloc[0])],
            popup=f"<strong>{etablissement_data['Nom_etablissement'].iloc[0]}</strong><br>{etablissement_data['Adresse_1'].iloc[0]}",
            tooltip=etablissement_data['Nom_etablissement'].iloc[0],
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)

    # Add markers for the addresses in gray
    for _, row in results.iterrows():
        if pd.notna(row['longitude']) and pd.notna(row['latitude']):
            if pd.isna(row['adresse']):
                row['adresse'] = ""
            folium.Marker(
                [float(row['latitude']), float(row['longitude'])],
                popup=f"<strong>{row['adresse']}</strong> <br>{row['city']}",
                tooltip=f"<strong>{row['adresse']}</strong> <br>{row['city']}",
                icon=folium.Icon(color='lightgray', icon='info-sign')
            ).add_to(m)

    # Adjust the view to fit all the markers
    if lats and lons:
        m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=[50, 50])
    return m

def geocode_addresses(df_code_rne):
    """
    Géocode les adresses selon le format exact de l'API
    """
    # S'assurer que les valeurs numériques sont converties en entiers sans décimales
    df_code_rne = df_code_rne.copy()
    
    # Gérer les NaN avant la conversion
    df_code_rne['postcode'] = df_code_rne['postcode'].fillna(0).astype(int).astype(str)
    df_code_rne['citycode'] = df_code_rne['citycode'].fillna(0).astype(int).astype(str)
    
    # Remplacer les '0' par une chaîne vide pour les valeurs qui étaient NaN
    df_code_rne['postcode'] = df_code_rne['postcode'].replace('0', '')
    df_code_rne['citycode'] = df_code_rne['citycode'].replace('0', '')

    # Conversion du DataFrame en CSV
    csv_buffer = StringIO()
    df_code_rne.to_csv(csv_buffer, index=False, encoding='utf-8')
    csv_string = csv_buffer.getvalue()

    # Construction de la requête multipart/form-data
    url = "https://api-adresse.data.gouv.fr/search/csv/"
    
    # Création des données multipart selon la documentation
    multi = {
        'data': ('addresses.csv', csv_string, 'text/csv'),
    }
    
    # Paramètres additionnels
    data = {
        'columns': ['adresse', 'city'],
        'citycode': 'citycode',
        'result_columns': ['latitude', 'longitude']
    }

    try:
        response = requests.post(url, files=multi, data=data)
        response.raise_for_status()
        
        return pd.read_csv(StringIO(response.text))
    except Exception as e:
        print(f"Erreur lors du géocodage : {str(e)}")
        return None

def perimetre_page():
    st.title("Périmètre de recrutement de l'établissement")
    
    df_etab, df = load_data_annuaire(), load_data()
    if df_etab is None or df is None:
        st.error("Impossible de charger les données")
        return
    
    # Ajout d'une valeur par défaut pour la ville
    etab_disponibles = ['Sélectionnez un établissement'] + sorted([str(etabb) for etabb in df_etab['etab_recherche'].unique()])
    etab_selectionnee = st.selectbox(
        "Rechercher un étalissement",
        options=etab_disponibles,
        index=0,
        key="etab_search"
    )

    # Ne garder que les lignes de df_etab['Identifiant_de_l_etablissement'] de etab_selectionnee == df['code_rne']
    df_code_rne = df[df['code_rne'].isin(df_etab[df_etab['etab_recherche'] == etab_selectionnee]['Identifiant_de_l_etablissement'])]
    
    # Supprimer les colonnes inutiles
    df_code_rne = df_code_rne.drop(columns=['code_region','libelle_region','code_academie','libelle_academie','code_departement','libelle_departement_eleve','numero_voie_et_cote', 'type_etablissement', 'code_rne', 'no_de_voie_debut', 'no_de_voie_fin', 'parite', 'ville_recherche'])

    # Renommer les colonnes
    df_code_rne = df_code_rne.rename(columns={'code_postal':'postcode', 'code_insee':'citycode','com_name_upper':'city','type_et_libelle':'adresse'})

    results = geocode_addresses(df_code_rne)
    if results is not None:
        st.subheader("Résultats de la recherche : " + str(len(results)) + " adresses/villes trouvées")
        
        #DEGUG
        # st.dataframe(results)
        # st.dataframe(df_etab[df_etab['etab_recherche'] == etab_selectionnee])

        st.subheader("Périmètre de recrutement de l'établissement")
        map = create_address_map(results, df_etab[df_etab['etab_recherche'] == etab_selectionnee])
        folium_static(map)
    
    elif etab_selectionnee != 'Sélectionnez un établissement':
        st.error("Données manquantes pour cet établissement. Essayez avec un autre établissement !")
