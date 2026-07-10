# Prompt - Ingest Python CSV vers SQL Server (7B-2)

Tu es un expert Python, pandas et SQL Server.

## Contexte

- Fichier source : `{csv_path}` (ex. `samples/data/superstore/Sample - Superstore.csv`)
- Serveur SQL : `{sql_server}` (ex. `localhost\SQLEXPRESS`)
- Base : `{database_name}` (ex. `POC_ETL_IA`)
- Table cible : `{target_table}` (ex. `raw_superstore`)
- Mapping colonnes CSV → SQL : `{column_mapping}`
- batch_id : `{batch_id}` (ex. `1`)
- source_system : `{source_system}` (ex. `KAGGLE_SUPERSTORE`)

## Objectif

Produire un script Python qui :

1. lit le CSV (gestion encodage et dates)
2. renomme / type les colonnes selon le mapping
3. charge en mode append ou truncate+load (parametrable)
4. affiche un resume : lignes chargees, clients distincts, produits distincts
5. géré les erreurs de connexion proprement (`pyodbc`)

## Contraintes

- Utiliser `pyodbc` ou `sqlalchemy` + `pandas`.
- Pas de credentials en dur : variables ou arguments CLI.
- Ne pas inventer de colonnes absentes du CSV fourni.
- Script exécutable : `python script.py --help`

## Sortie attendue

1. Script Python complet
2. Exemple de commande d'exécution
3. Requêtes SQL de vérification post-ingest
4. Hypotheses et limites

## Exemple de variables (cas Superstore)

```
csv_path = samples/data/superstore/Sample - Superstore.csv
target_table = raw_superstore
column_mapping = Row ID→row_id, Order ID→order_id, Customer ID→customer_id, ...
```
