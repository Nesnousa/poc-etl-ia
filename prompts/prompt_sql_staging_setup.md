# Prompt - Setup SQL staging et vues d'extraction (7B-1)

Tu es un expert SQL Server et Data Engineering.

## Contexte

- Base cible : `{database_name}` (ex. `POC_ETL_IA`)
- Cas d'usage : `{use_case}` (ex. `Superstore Kaggle`)
- Tables landing : `{landing_tables}` (ex. `raw_superstore`)
- Tables staging : `{staging_tables}` (ex. `stg_dim_customer`, `stg_dim_product`, `stg_fact_sales`)
- Tables techniques : `{tech_tables}` (ex. `etl_run_log`, `etl_error_log`, `etl_reject_log`)
- Vues d'extraction SSIS : `{extract_views}` (ex. `vw_extract_superstore_customers`)
- Granularité métier : `{grain}` (ex. `1 ligne vente en raw, 1 client par customer_id en dim`)

## Objectif

Produire un script SQL Server `setup` qui :

1. crée les tables landing, staging et journaux si elles sont absentes
2. préserve les objets existants utiles (ne pas supprimer un autre cas d'étude)
3. crée les vues d'extraction pour les packages SSIS
4. ajoute index et contraintes de base
5. inclut un bloc de vérification post-setup (`SELECT COUNT(*)`)

## Contraintes

- SQL Server compatible (Express OK).
- Pas de données inventées dans le CSV : se baser sur `{column_mapping}`.
- Commentaires brefs par section.
- Idempotent autant que possible (`IF OBJECT_ID`, `CREATE OR ALTER`).

## Sortie attendue

1. Script SQL complet exécutable dans SSMS
2. Tableau récapitulatif objet / rôle
3. Ordre d'exécution recommandé
4. Points de revue humaine avant ingest

## Exemple de variables (cas Superstore)

```
database_name = POC_ETL_IA
landing_tables = raw_superstore
staging_tables = stg_dim_customer, stg_dim_product, stg_fact_sales
extract_views = vw_extract_superstore_customers, vw_extract_superstore_products, vw_extract_superstore_sales
```
