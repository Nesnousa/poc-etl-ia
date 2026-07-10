# Prompt - Package SSIS dimension (7B-3 / 7B-4)

Tu es un expert SSIS, SQL Server et Data Engineering.

## Contexte

- Package : `{package_name}` (ex. `PKG_DIM_CUSTOMER` ou `PKG_DIM_PRODUCT`)
- Source : `{source_view}` (ex. `vw_extract_superstore_customers`)
- Cible : `{target_table}` (ex. `stg_dim_customer`)
- Cle métier : `{business_key}` (ex. `customer_id` ou `product_id`)
- batch_id : `{batch_id}` (ex. `1`)
- source_system : `{source_system}` (ex. `KAGGLE_SUPERSTORE`)
- Règles métier : `{business_rules}` (ex. dedupe par cle, rejeter nom vide)
- Logging : tables `{log_tables}` (ex. `etl_run_log`, `etl_reject_log`, `etl_error_log`)

## Objectif

Proposer un package SSIS réutilisable pour charger une **dimension** :

### Control Flow

1. `SQL_StartRun` → `usp_log_etl_run_start`
2. `SQL_CountSource` → compte lignes source
3. `SQL_LogRejects` → ecrit rejets dans `etl_reject_log`
4. `DFT_LoadDimension` → flux de données
5. `SQL_EndRunSuccess` → `usp_log_etl_run_end`
6. `OnError` → `etl_error_log`

### Data Flow (pattern validé POC)

- Preferer **transformations en SQL** dans OLE DB Source (GROUP BY, HAVING, TRIM)
- Eviter Derived Column / Conditional Split si génération XML fragile
- `OLE DB Source` → `Row Count` → `OLE DB Destination`

## Contraintes

- Ne pas inventer de metadonnees absentes.
- Documenter les GUID, connexion `CM_POC_ETL_IA`, variables `RunId`, `RowCountIn`, `RowCountOut`.
- Inclure script reset staging et script validation SQL.
- Sortie lisible par un developpeur (pas seulement XML brut si possible : pseudo-code + SQL source).

## Sortie attendue

1. Description du package et ordre d'exécution
2. Requête SQL source complete (dedupe + filtre + metadonnees)
3. Requête SQL_LogRejects
4. Liste des colonnes destination
5. Scripts reset / validate associes
6. Points de revue humaine (Visual Studio, pas seulement dtexec Express)

## Exemple Superstore — PKG_DIM_CUSTOMER

```
source_view = vw_extract_superstore_customers
target_table = stg_dim_customer
business_key = customer_id
business_rules = GROUP BY customer_id; rejeter customer_name vide; customer_name_clean = LTRIM(RTRIM(...))
```

## Exemple Superstore — PKG_DIM_PRODUCT

```
source_view = vw_extract_superstore_products
target_table = stg_dim_product
business_key = product_id
business_rules = GROUP BY product_id; rejeter product_name vide
```
