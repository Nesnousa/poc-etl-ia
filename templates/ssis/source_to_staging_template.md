# Template générique — Package SSIS « Source vers Staging »

## Objectif

Charger n'importe quelle source (base, fichier, vue) vers une table de staging SQL Server, avec journalisation et contrôles de base. Réutilisable sur tout projet ETL.

## Variables à remplacer

- `{nom_package}` → nom du package, ex. `PKG_DIM_CUSTOMER`
- `{source}` → connexion / objet source, ex. `vw_extract_customers`
- `{table_staging}` → table cible, ex. `stg_dim_customer`
- `{source_system}` → système source, ex. `KAGGLE_SUPERSTORE`

## Structure du package

### Control Flow (flux de contrôle)

1. `Exécuter SQL` — démarrage du lot : appelle `usp_log_etl_run_start` → récupère un `batch_id`.
2. `Data Flow Task` — extraction et chargement (voir ci-dessous).
3. `Exécuter SQL` — clôture du lot : appelle `usp_log_etl_run_end` (statut SUCCESS, nombre de lignes).
4. `Gestionnaire d'événement OnError` — écriture dans `etl_error_log`.

### Data Flow (flux de données)

1. **Source** — lecture depuis `{source}`.
2. **Data Conversion** — alignement des types si nécessaire.
3. **Derived Column** — ajout des colonnes techniques : `batch_id`, `source_system` = `{source_system}`, `source_extract_ts`, `load_ts`.
4. **Lookup** (optionnel) — vérification des clés vers les dimensions ; lignes non trouvées → rejet.
5. **OLE DB Destination** — insertion dans `{table_staging}`.

## Paramètres du package

- `source_connection`
- `target_connection`
- `batch_id`
- `source_system`
- `package_name`

## Contrôles minimums (avant de valider le package)

- Vérifier le nombre de lignes chargées (entrée vs sortie).
- Vérifier que les champs obligatoires ne sont pas NULL.
- Vérifier l'absence de doublons techniques.
- Vérifier que le run est bien tracé dans `etl_run_log` (statut SUCCESS).

## Résultat attendu

Un package réutilisable pour la majorité des chargements « source → staging », personnalisable par source et par schéma, avec journalisation et gestion d'erreurs intégrées.
