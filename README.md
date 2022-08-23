# OpenStreetMap - Recycling points for Métropole Nice Côte d'Azur
Script for gathering recycling points from the Nice Open-Data API in OSM-compatible format

http://opendata.nicecotedazur.org/data/dataset/cartographie-des-points-d-apport-volontaire-tri-des-dechets-points-de-recyclage

## What this script does:
* Matches city names between OSM & API
* Filters out incomplete data
* Aggregates different recycling types for each recycling location
* Selects recycling points by city
* Separates recycling points not already mapped in OSM from others
* Outputs a csv file that can be imported in JOSM for validation

## How to use this script:
Some variables need to be setup manually for the script to run:
* project_folder | Folder location of the script
* api_json | API geojson filename (needs to be in same folder as script)
* city_name | Defines which city to work on

# OpenStreetMap - Points de recyclage pour la Métropole Nice Côte d'Azur
Script d'agrégation des points de recyclages de l'API Open-Data Nice au format OSM

http://opendata.nicecotedazur.org/data/dataset/cartographie-des-points-d-apport-volontaire-tri-des-dechets-points-de-recyclage

## À quoi sert ce script :
* Correspondance des noms de villes entre OSM & API
* Filtre les données incomplètes
* Agrège différents types de recyclage pour chaque localisation
* Sélectionne les points de recyclage par ville
* Sépare les points de recyclage non-cartographié dans OSM du reste
* Retourne un fichier csv qui peut être importé dans JOSM pour validation

## Comment utiliser ce script:
Certaines variables doivent être définies manuellement pour que le script fonctionne :
* project_folder | Dossier dans lequel le script se trouve
* api_json | Nom du fichier API geojson (il doit se trouver dans le même dossier que le script)
* city_name | Ville sur laquelle on travaille
