from pathlib import Path
import pandas as pd
import numpy as np

# --- 1. CONFIGURATION DES CHEMINS (Pathlib) ---
# Utilisation de Pathlib pour gérer les chemins de manière indépendante du système d'exploitation
PROJECT_ROOT = Path(__file__).parent.parent 
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "raw_logs"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Créer le dossier de sortie s'il n'existe pas
OUTPUT_DIR.mkdir(exist_ok=True)


# --- 2. FONCTION DE NETTOYAGE CSV (Exercice 1) ---

def clean_and_save_csv(input_file: Path, output_file: Path):
    """
    Lit un CSV, nettoie les données, convertit les types (transforme les invalides en NaN), 
    puis supprime les lignes avec des NaN critiques et sauvegarde le résultat.
    """
    print(f"--- Nettoyage de {input_file.name} ---")

    # A. Chargement du fichier
    try:
        df = pd.read_csv(
            input_file,
            sep=";",              
            dtype=str,            
            encoding="utf-8",     
            keep_default_na=False, 
            on_bad_lines='skip'   # Ignore les lignes mal formatées (qui n'ont pas le bon nombre de séparateurs)
        )
    except FileNotFoundError:
        print(f"Erreur : Le fichier {input_file} n'a pas été trouvé. Vérifiez son chemin.")
        return
    
    initial_rows = len(df)
    
    # B. Nettoyage des Noms de Colonnes
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # C. Préparation des Valeurs Manquantes
    # Remplacer les chaînes vides, 'N/A', etc. par le marqueur standard 'np.nan'
    df = df.replace({"": np.nan, "N/A": np.nan, "NA": np.nan, " ": np.nan})
    
    # -------------------------------------------------------------------------
    # ✅ ÉTAPE D : CONVERSION ET VALIDATION DES TYPES (TRANSFORME INVALIDE -> NaN)
    # -------------------------------------------------------------------------

    # 1. Nettoyage de 'montant_total_eur'
    if 'montant_total_eur' in df.columns:
        df['montant_total_eur'] = (
            df['montant_total_eur']
            .astype(str)
            .str.replace(r'[€" ]', '', regex=True) # Supprime € et espaces
            .str.replace(',', '.')                 # Convertit virgule décimale en point
        )
        # Convertit en nombre. Toute valeur non convertible (ex: 'XYZ', 'inf') devient np.nan ici.
        df['montant_total_eur'] = pd.to_numeric(df['montant_total_eur'], errors='coerce')
        
    # 2. Nettoyage de 'age'
    if 'age' in df.columns:
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
        # Les âges négatifs ou irréalistes (> 100) deviennent NaN, ce qui les marquent pour la suppression
        df.loc[df['age'] < 0, 'age'] = np.nan
        df.loc[df['age'] > 100, 'age'] = np.nan
        # Utilisation de pd.Int64Dtype() pour gérer les entiers avec des valeurs NaN
        df['age'] = df['age'].round().astype(pd.Int64Dtype(), errors='ignore')

    # 3. Conversion des dates
    date_cols = ['date_inscription', 'derniere_connexion']
    for col in date_cols:
        if col in df.columns:
            # Si une date est mal formatée, elle devient NaT (l'équivalent de NaN pour les dates)
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)

    # -------------------------------------------------------------------------
    # ✅ ÉTAPE E : FILTRAGE FINAL (SUPPRIME LES VIDES ET LES INVALIDES MAINTENANT MARQUÉS COMME NaN)
    # -------------------------------------------------------------------------

    # 1. Suppression des lignes où TOUTES les colonnes sont manquantes
    df = df.dropna(how="all")
    print(f"-> {initial_rows - len(df)} lignes entièrement vides supprimées.")
    
    # 2. Définition des critères critiques.
    # Note : 'montant_total_eur' ou 'age' sont maintenant np.nan s'ils étaient invalides/mal formatés.
    critical_cols = ['id_client', 'nom', 'montant_total_eur', 'age'] 
    
    pre_drop_rows = len(df)
    
    # Supprime toute ligne où AU MOINS UNE des colonnes critiques est NaN.
    df = df.dropna(subset=critical_cols, how='any') 
    
    dropped_rows = pre_drop_rows - len(df)
    print(f"-> {dropped_rows} lignes supprimées car une donnée critique était manquante ou invalide.")
    
    # F. Sauvegarde
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"✅ Nettoyage CSV terminé. {len(df)} lignes conservées. Sauvé dans {output_file}")


# --- 3. FONCTION DE TRAITEMENT DE LOGS (Exercice 2) ---

def collect_errors(log_dir: Path, output_file: Path):
    """Parcourt tous les fichiers .log et centralise les lignes 'ERROR'."""
    print(f"\n--- Traitement des logs dans {log_dir.name} ---")

    error_count = 0
    # Ouvre le fichier de sortie en mode écriture ('w')
    with output_file.open("w", encoding="utf-8") as out:
        # Parcours tous les fichiers finissant par .log dans le dossier des logs
        for log_file in log_dir.glob("*.log"):
            try:
                # Lit tout le texte du fichier log et le divise en lignes
                for line in log_file.read_text(encoding="utf-8").splitlines():
                    # Vérifie si la ligne contient le mot 'ERROR'
                    if "ERROR" in line:
                        # Écrit la ligne dans le fichier de sortie, en ajoutant le nom du fichier source
                        out.write(f"{log_file.name}: {line}\n")
                        error_count += 1
            except Exception as e:
                print(f"⚠️ Erreur de lecture du log {log_file.name}: {e}")

    print(f"✅ Traitement des logs terminé. {error_count} erreurs trouvées. Sauvé dans {output_file}")


# --- 4. POINT D'ENTRÉE PRINCIPAL ---

if __name__ == "__main__":
    # Définition des chemins exacts d'entrée et de sortie
    input_csv = DATA_DIR / "data.csv"
    output_csv = OUTPUT_DIR / "clean_data.csv"
    output_errors = OUTPUT_DIR / "errors.log"

    # Exécution des fonctions
    clean_and_save_csv(input_csv, output_csv)
    collect_errors(LOGS_DIR, output_errors)