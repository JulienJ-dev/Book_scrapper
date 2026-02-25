# Books to Scrape – Pipeline ETL en Python

## Description du projet

Ce projet met en place un pipeline ETL (Extract – Transform – Load) à partir du site :

https://books.toscrape.com

Le script parcourt toutes les catégories du site, gère l'aspect multi-pages, extrait les informations demandées de chaque livre, télécharge les images associées et génère un fichier CSV par catégorie.

Repository GitHub :  
https://github.com/JulienJ-dev/Book_scrapper

## Pipeline ETL

### Extract

#### Récupération de toutes les catégories depuis la page d’accueil
#### Gestion automatique de la pagination
#### Accès à chaque page produit
#### Extraction des données suivantes :

- url    
- categorie
- titre
- description  
- url image  
- UPC
- Prix HT
- Prix TTC  
- Disponibilité
- notation

### Transform
- Conversion des prix en float  
- Conversion de la disponibilité en entier  
- Nettoyage des caractères interdits dans les noms de fichiers image  
- Structuration des données sous forme d'un tableau de dictionnaires

### Load
- Génération d’un fichier CSV par catégorie  
- Téléchargement des images de couverture  
- Organisation automatique des dossiers de sortie  

## Installation

### Cloner le repository en saisissant dans le terminal ligne par ligne :

git clone https://github.com/JulienJ-dev/Book_scrapper.git

cd Book_scrapper

python -m venv .venv

.venv\Scripts\activate

python.exe -m pip install --upgrade pip

pip install -r requirements.txt

## Lancement du programme

### Toujours dans le terminal, saisir : 

python main_scrapping_books_toscrape.py

## Déroulé du programme

Le programme récupère les données et indique un pourcentage de progression général et par catégorie.

Deux fichiers seront créés à la racine du fichier "Book_Scrapper_Script" :

- "Books_toscrape_datas" : contenant les fichiers csv par catégorie contenant les données scrappées

- "Books_visuals" : contenant les visuels des produits scrappés
