import streamlit as st

def legal_page():
    st.title("Mentions légales")

    st.markdown("""
    ### Éditeur
    Cette application est éditée dans le cadre d'un projet étudiant pour la formation M2 MIASHS à l'Université Paul-Valéry Montpellier 3 par Thomas Ayrivié.

    ### Hébergement
    Application hébergée sur Streamlit Cloud
    San Francisco, CA 94107
    United States.

    ### Données personnelles
    Cette application n'effectue aucune collecte de données personnelles.
    Les données affichées sont issues de sources publiques (open data) fournies par la Région académique Occitanie et la BAN - Base des adresses nationales. Voir la section À propos pour plus d'informations.

    ### Cookies
    Cette application n'utilise pas de cookies.

    ### Propriété intellectuelle
    Le [code source](https://github.com/ThomasAyr/carte_scolaire_dev) de cette application est soumis à la licence MIT.
    Les données utilisées sont sous licence ouverte.                 

    ### Contact
    Pour toute question concernant l'application :
    - Email : [thomas.ayrivie@etu.univ-montp3.fr](mailto:thomas.ayrivie@etu.univ-montp3.fr)
    - Formation MIASHS de l'UFR 6, Université Paul-Valéry Montpellier 3, Route de Mende, 34199 Montpellier Cedex 5
    """)

    st.info('NB : Ces mentions légales sont fournies à titre indicatif dans le cadre d\'un projet étudiant.')
