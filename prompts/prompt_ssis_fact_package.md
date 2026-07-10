# Prompt - Package SSIS fait / table de faits (7B-4)

Tu es un expert SSIS, SQL Server et modélisation en etoile.

## Contexte

- Package : `{package_name}` (ex. `PKG_FACT_SALES`)
- Source : `{source_view}` (ex. `vw_extract_superstore_sales`)
- Cible : `{target_table}` (ex. `stg_fact_sales`)
- Dimensions prerequises : `{dimension_tables}` (ex. `stg_dim_customer`, `stg_dim_product`)
- Cles de jointure : `{join_keys}` (ex. `customer_id`, `product_id`)
- Mesures : `{measures}` (ex. `sales`, `quantity`, `discount`, `profit`)
- Colonnes calculees : `{calculated_columns}` (ex. `margin_pct = profit / sales si sales <> 0`)
- batch_id : `{batch_id}`
- Logging : `{log_tables}`

## Objectif

Proposer un package SSIS pour charger une **table de faits** :

### Règles métier

- Lookup dimensions : vérifier que `{join_keys}` existent en staging
- Rejeter ou exclure les lignes sans dimension (journal `etl_reject_log`)
- Calculer `{calculated_columns}` en SQL source si possible

### Control Flow

Même logique que le package dimension : StartRun → CountSource → LogRejects → DFT → EndRunSuccess → OnError

### Data Flow

- OLE DB Source avec `INNER JOIN` sur dimensions (remplacé Lookup SSIS fragile en XML)
- Row Count + OLE DB Destination

## Contraintes

- Ordre d'exécution : dimensions chargees **avant** le fait.
- Ne pas inventer de colonnes.
- Reconciliation volume : fait vs raw documentee.
- Inclure reset + validation SQL (cles orphelines = 0).

## Sortie attendue

1. Requête SQL source (JOIN + margin_pct)
2. Requête SQL_LogRejects (LEFT JOIN pour détecter orphelins)
3. Structure Control Flow / Data Flow
4. Scripts reset / validate
5. Points de revue humaine

## Exemple Superstore — PKG_FACT_SALES

```
source_view = vw_extract_superstore_sales
target_table = stg_fact_sales
dimension_tables = stg_dim_customer (batch_id=1), stg_dim_product (batch_id=1)
calculated_columns = margin_pct = CASE WHEN sales <> 0 THEN profit/sales ELSE NULL END
volume_attendu = ~9994 lignes
```
