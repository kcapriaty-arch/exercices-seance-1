# Mini-projet : Nettoyage de Données et Traitement de Logs (Séance 1)

Ce projet réalise le nettoyage d'un fichier CSV (data/data.csv) et la centralisation des erreurs issues de fichiers de logs (raw_logs/).

## Structure du Projet

- `data/`: Fichiers d'entrée CSV.
- `raw_logs/`: Fichiers de logs d'entrée.
- `src/main.py`: Point d'entrée unique, effectuant le parsing CSV et le traitement des logs.
- `output/`: Dossier généré pour les résultats (`clean_data.csv`, `errors.log`).

## Installation et Lancement

Le projet est géré avec `uv` pour garantir l'isolation et la reproductibilité.

1.  **Synchronisation de l'environnement virtuel et installation des dépendances (pandas, numpy) :**
    ```bash
    uv sync
    ```
2.  **Exécution du script principal :**
    ```bash
    uv run python src/main.py
    ```

### Résultat
Les fichiers de sortie se trouvent dans le dossier `output/`.