# SectoAppli - Carte Scolaire Occitanie

## Description
Application web permettant de visualiser la sectorisation des établissements scolaires (collèges et lycées) en Occitanie. Développée avec Streamlit, elle offre une interface intuitive pour rechercher et consulter les informations sur les établissements scolaires.

## Fonctionnalités
- 🔍 Recherche d'établissements par ville
- 🗺️ Visualisation cartographique des établissements
- 📊 Statistiques détaillées par département
- 🏫 Informations complètes sur chaque établissement
- 📍 Sectorisation détaillée

## Installation

```bash
# Cloner le repository
git clone https://github.com/ThomasAyr/carte_scolaire_dev.git
cd carte_scolaire_dev

# Créer et activer un environnement virtuel (optionnel mais recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
streamlit run main.py
```

## Sources de données
- Carte scolaire : data.occitanie.education.gouv.fr
- Annuaire des établissements : API Education Nationale
- Géocodage : Base Adresse Nationale (BAN)

## Technologies utilisées
- Streamlit
- Pandas
- Folium
- Plotly
- Requests

## Auteur
Thomas Ayrivié - M2 MIASHS - Université Paul-Valéry Montpellier 3

## Licence
MIT License
