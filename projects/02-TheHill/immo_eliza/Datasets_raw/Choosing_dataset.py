import pandas as pd
import os
from datetime import datetime

def explorer_dataset(chemin_fichier, nom_dataset, fichier_sortie=None):
    resultats = []
    resultats.append(f"\n{'='*50}")
    resultats.append(f"ANALYSE DU DATASET: {nom_dataset}")
    resultats.append(f"{'='*50}\n")
    
    # Essayer différents délimiteurs et encodages courants
    delimiteurs = [',', ';', '\t', '|']
    encodages = ['utf-8', 'latin1', 'ISO-8859-1']
    
    df = None
    successful_params = {}
    
    # Tenter de lire le fichier avec différentes combinaisons de paramètres
    for delimiteur in delimiteurs:
        for encodage in encodages:
            try:
                df = pd.read_csv(chemin_fichier, delimiter=delimiteur, encoding=encodage, 
                                 on_bad_lines='skip', low_memory=False)
                successful_params = {"delimiter": delimiteur, "encoding": encodage}
                break
            except Exception as e:
                continue
        if df is not None:
            break
    
    # Si toutes les tentatives ont échoué
    if df is None:
        erreur = f"Impossible de lire le fichier {nom_dataset}. Veuillez vérifier son format."
        resultats.append(erreur)
        print(erreur)
        
        if fichier_sortie:
            with open(fichier_sortie, 'a', encoding='utf-8') as f:
                for ligne in resultats:
                    f.write(ligne + "\n")
        return None
    
    # Indiquer les paramètres qui ont fonctionné
    resultats.append(f"Fichier chargé avec: délimiteur='{successful_params['delimiter']}', encodage='{successful_params['encoding']}'")
    
    # INFORMATIONS CLÉS SEULEMENT
    resultats.append(f"Nombre total de propriétés: {len(df)}")
    resultats.append(f"Nombre de colonnes: {len(df.columns)}")
    
    # Liste des colonnes (présentée plus proprement)
    resultats.append("\nCOLONNES DISPONIBLES:")
    # Afficher les colonnes sur plusieurs lignes pour plus de lisibilité
    cols_per_line = 4
    for i in range(0, len(df.columns), cols_per_line):
        resultats.append("  " + ", ".join(df.columns[i:i+cols_per_line]))
    
    # Valeurs manquantes - afficher seulement le nombre total et le pourcentage
    total_missing = df.isnull().sum().sum()
    missing_percent = (total_missing / (len(df) * len(df.columns))) * 100
    resultats.append(f"\nValeurs manquantes: {total_missing} ({missing_percent:.2f}% du total)")
    
    # Top 5 des colonnes avec le plus de valeurs manquantes (si applicable)
    missing_cols = df.isnull().sum()
    if missing_cols.max() > 0:
        resultats.append("Top 5 des colonnes avec valeurs manquantes:")
        for col, count in missing_cols.sort_values(ascending=False).head(5).items():
            if count > 0:
                percent = (count / len(df)) * 100
                resultats.append(f"  {col}: {count} valeurs manquantes ({percent:.2f}%)")
    
    # Statistiques sur le prix (si disponible)
    price_cols = [col for col in df.columns if 'price' in col.lower() or 'prix' in col.lower()]
    if price_cols:
        price_col = price_cols[0]
        try:
            resultats.append(f"\nSTATISTIQUES DE PRIX ({price_col}):")
            resultats.append(f"  Min: {df[price_col].min()}")
            resultats.append(f"  Max: {df[price_col].max()}")
            resultats.append(f"  Moyenne: {df[price_col].mean():.2f}")
            resultats.append(f"  Médiane: {df[price_col].median()}")
        except:
            resultats.append(f"  Impossible de calculer les statistiques de prix - vérifier le type de données")
    
    # Répartition géographique
    location_cols = [col for col in df.columns if any(term in col.lower() for term in 
                    ['local', 'ville', 'city', 'location', 'postal', 'code', 'zip', 'commune', 'region'])]
    if location_cols:
        location_col = location_cols[0]
        resultats.append(f"\nRÉPARTITION GÉOGRAPHIQUE ({location_col}):")
        resultats.append(f"  Nombre de localités différentes: {df[location_col].nunique()}")
        resultats.append("  Top 5 des localités:")
        top_locations = df[location_col].value_counts().head(5)
        for loc, count in top_locations.items():
            percent = (count / len(df)) * 100
            resultats.append(f"    {loc}: {count} ({percent:.2f}%)")
    
    # Types de biens
    type_cols = [col for col in df.columns if any(term in col.lower() for term in 
                ['type', 'property', 'bien', 'building', 'categ'])]
    if type_cols:
        type_col = type_cols[0]
        resultats.append(f"\nTYPES DE BIENS ({type_col}):")
        type_counts = df[type_col].value_counts().head(8)  # Limiter aux 8 plus fréquents
        for type_bien, count in type_counts.items():
            percent = (count / len(df)) * 100
            resultats.append(f"  {type_bien}: {count} ({percent:.2f}%)")
    
    # Afficher les résultats dans la console
    for ligne in resultats:
        print(ligne)
    
    # Enregistrer les résultats dans un fichier si demandé
    if fichier_sortie:
        with open(fichier_sortie, 'a', encoding='utf-8') as f:
            for ligne in resultats:
                f.write(ligne + "\n")
    
    return df

# Définir le chemin de base
chemin_base = "g:/Mon Drive/BeCode/Bootcamp AI/LGG-Thomas5/projects/02-TheHill/immo_eliza/Datasets_raw/"

# Créer un fichier de sortie avec la date pour éviter d'écraser d'anciens résultats
date_actuelle = datetime.now().strftime("%Y-%m-%d_%H-%M")
fichier_resultats = chemin_base + f"analyse_synthese_{date_actuelle}.txt"

# Écrire un en-tête dans le fichier
with open(fichier_resultats, 'w', encoding='utf-8') as f:
    f.write(f"SYNTHÈSE COMPARATIVE DES DATASETS - {date_actuelle}\n")
    f.write("="*50 + "\n\n")

# Explorer chaque dataset et enregistrer les résultats
df1 = explorer_dataset(chemin_base + "Cheetah.csv", "Dataset Cheetah", fichier_resultats)
df2 = explorer_dataset(chemin_base + "Dolphin.csv", "Dataset Dolphin", fichier_resultats)
df3 = explorer_dataset(chemin_base + "Elephant.csv", "Dataset Elephant", fichier_resultats)
df4 = explorer_dataset(chemin_base + "Giraffe.csv", "Dataset Giraffe", fichier_resultats)
df5 = explorer_dataset(chemin_base + "Kangaroo.csv", "Dataset Kangaroo", fichier_resultats)
df6 = explorer_dataset(chemin_base + "Koala.csv", "Dataset Koala", fichier_resultats)
df7 = explorer_dataset(chemin_base + "Panda.csv", "Dataset Panda", fichier_resultats)
df8 = explorer_dataset(chemin_base + "Penguin.csv", "Dataset Penguin", fichier_resultats)
df9 = explorer_dataset(chemin_base + "Tiger.csv", "Dataset Tiger", fichier_resultats)
df10 = explorer_dataset(chemin_base + "Unicorn.csv", "Dataset Unicorn", fichier_resultats)

print(f"\n🎉 Analyse terminée! Les résultats ont été enregistrés dans:\n{fichier_resultats}")
