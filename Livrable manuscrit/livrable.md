# SectoAppli - Visualisation de la carte scolaire en Occitanie

## Contexte et objectifs

Dans le cadre de mon alternance au rectorat académique d'Occitanie, j'ai participé activement à la valorisation des données de la carte scolaire via leur publication en open data.
Cette démarche s'inscrit dans un défi national porté par data.gouv.fr, qui souligne la difficulté actuelle des parents à identifier les établissements de secteur de leurs enfants, les informations étant souvent dispersées et peu accessibles. Les représentations cartographiques existantes restent partielles et principalement locales. [Lien du défi](https://defis.data.gouv.fr/defis/carte-scolaire)

## Solution innovante

Pour répondre à ces enjeux, j'ai développé une application web qui propose une double approche :

### Interface grand public

L'application offre aux familles une interface intuitive leur permettant de localiser rapidement leur établissement de secteur. Cette interface se distingue du jeu de données brut par sa simplicité d'utilisation et sa visualisation cartographique interactive. Les utilisateurs peuvent ensuite accéder à des informations pertinentes concernant les établissements, les services proposés et coordonnées complètes.

### Tableau de bord administratif

L'application intègre également un outil d'analyse destiné aux services administratifs. Ce tableau de bord permet notamment :

- L'identification précise des zones où les données sont manquantes ou incomplètes
- Le suivi des secteurs à sectorisation multiple
- L'analyse fine de la répartition territoriale des établissements
  Ces indicateurs constituent un support pour l'évaluation et l'ajustement des politiques éducatives.

## Architecture technique

L'application s'appuie sur trois sources de données complémentaires :

- Les données de sectorisation issues de la plateforme open data de la région académique Occitanie
- L'annuaire des établissements accessible via l'API de l'Éducation Nationale
- Le service de géocodage de la Base Adresse Nationale

La stack technique a été choisie pour sa robustesse et sa maintenabilité :

- Streamlit pour l'interface utilisateur, permettant un développement rapide et efficace
- Plotly et Folium pour des visualisations interactives de qualité
- Pandas pour le traitement optimisé des données
- Streamlit Cloud pour un déploiement simplifié et scalable

## Perspectives d'évolution

Les principaux axes d'amélioration identifiés sont :

### Enrichissement géographique

La génération automatique des géométries de secteur constitue un enjeu majeur. En convertissant les listes de rues en polygones précis, nous pourrons intégrer automatiquement les nouvelles adresses dans la carte scolaire.

### Qualité des données

Un système de redressement des adresses permettrait d'améliorer significativement la qualité des données existantes. Ce système pourrait être couplé à des alertes automatiques signalant les incohérences dans les données.

### Extensions fonctionnelles

Le projet pourrait être enrichi par :

- L'extension du périmètre à d'autres académies
- L'intégration de données démographiques pour une analyse prospective
- Des outils de simulation pour optimiser les évolutions de sectorisation

## Impact et résultats

Cette application répond aux deux objectifs majeurs du **défi data.gouv.fr** :

1. Faciliter l'accès des parents à l'information sur la sectorisation scolaire
2. Fournir aux administrations des outils efficaces de pilotage territorial

Au-delà de ces objectifs initiaux, l'application contribue à la transparence des politiques éducatives et offre un support précieux pour l'analyse de la mixité sociale dans les établissements.
