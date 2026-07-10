# Prompt - Modèle Power BI sur staging SQL (Phase 9)

Tu es un expert Power BI, modélisation tabulaire et SQL Server.

## Contexte

- Serveur : `{sql_server}` (ex. `NESNOUSSA\SQLEXPRESS`)
- Base : `{database_name}` (ex. `POC_ETL_IA`)
- Tables fait : `{fact_table}` (ex. `stg_fact_sales`)
- Tables dimensions : `{dimension_tables}` (ex. `stg_dim_customer`, `stg_dim_product`)
- Relations : `{relationships}` (ex. fact.customer_id → dim.customer_id, fact.product_id → dim.product_id)
- Besoins métier : `{business_needs}` (ex. ventes par région, marge, top produits)

## Objectif

Produire un guide de construction du modèle Power BI :

1. Import Power Query (M) pour chaque table
2. Schéma des relations (cardinalité, direction du filtre)
3. Colonnes a masquer (batch_id, load_ts si non utiles en visuel)
4. 5 mesures DAX prioritaires
5. 3 visuels recommandes pour la demo POC
6. Contrôles : totaux cohérents avec SQL (`SUM(sales)` ~ staging)

## Contraintes

- Ne pas inventer de tables/colonnes absentes.
- Mode Import (pas DirectQuery sauf si demande).
- Expliquer le contexte de filtre pour chaque mesure.
- Indiquer les validations humaines post-import.

## Sortie attendue

1. Étapes Power BI Desktop (import → relations → mesures → visuels)
2. Scripts M ou instructions Get Data
3. Liste mesures DAX (renvoyer au prompt DAX pour le detail)
4. Requêtes SQL de contrôle croise
5. Points de revue humaine

## Exemple Superstore

```
fact_table = stg_fact_sales
dimension_tables = stg_dim_customer, stg_dim_product
business_needs = CA total, profit total, marge %, ventes par région, top 10 produits
```
