import streamlit as st

def about_page():
    st.title("À propos")
    st.markdown("""
    Cette application permet de rechercher des établissements scolaires en Occitanie.
    
    Cette architecture permet de fournir aux utilisateurs un outil complet pour :
    - Identifier le(s) établissement(s) de secteur des élèves d'Occitanie
    - Accéder aux informations détaillées de ces établissements
    - Visualiser leur localisation sur une carte interactive
    - Visualiser les manques de données et la politique éducative de la région

    Notre application combine trois sources de données, décrites ci-après, pour fournir un service complet à ses usagers.
    """)
    
    st.title("Sources de données")
    st.header("1. Carte scolaire des établissements publics d'Occitanie")

    st.subheader("Source principale")
    st.markdown("""
        - **Jeu de données** : Carte scolaire des collèges, lycées publics de la région Occitanie Rentrée 2024
        - **Fournisseur** : Région académique Occitanie
        """)
    st.markdown("[Accéder aux données](https://data.occitanie.education.gouv.fr/explore/dataset/fr-en-occitanie-carte-scolaire-des-colleges-lycees-publics/)")

    st.markdown("""
    Ce jeu de données est fondamental pour notre application car il contient la sectorisation 
    complète des établissements scolaires en Occitanie. Il résulte de l'agrégation des 13 fichiers 
    départementaux utilisés par les DSDEN (Directions des Services Départementaux de l'Éducation 
    Nationale) pour déterminer automatiquement le ou les établissements de secteur des élèves.
    """)

    st.subheader("Contexte réglementaire")
    st.markdown("""
    La sectorisation des établissements publics est régie par différentes autorités :
    - Pour les **collèges** : Le conseil départemental définit les secteurs de recrutement, 
      pouvant inclure des "secteurs multi-collèges" pour favoriser la mixité sociale.
    - Pour les **lycées** : Le conseil régional, en collaboration avec l'autorité académique, 
      définit les districts de recrutement en considérant les critères démographiques, 
      économiques et sociaux.
    """)

    st.header("2. Annuaire de l'éducation")

    st.subheader("Source des données détaillées")
    st.markdown("""
        - **API** : Annuaire de l'éducation
        - **Usage** : Enrichissement des informations établissements
        """)
    st.markdown("[Accéder à l'API](https://data.occitanie.education.gouv.fr/explore/dataset/fr-en-annuaire-education/)")

    st.markdown("""
    Cette API nous permet d'enrichir notre application avec des informations détaillées 
    sur chaque établissement :
    - Coordonnées complètes
    - Services disponibles (restauration, internat...)
    - Options et sections spéciales
    - Contacts et informations pratiques
    """)

    st.header("3. Base Adresse Nationale (BAN)")

    st.subheader("Source de géocodage")
    st.markdown("""
        - **API** : API Adresse (Base Adresse Nationale)
        - **Usage** : Géocodage des adresses
        """)
    st.markdown("[Accéder à l'API](https://api.gouv.fr/les-api/base-adresse-nationale)")

    st.markdown("""
    La BAN est utilisée pour :
    - Convertir les adresses en coordonnées géographiques
    - Permettre la visualisation cartographique
    """)