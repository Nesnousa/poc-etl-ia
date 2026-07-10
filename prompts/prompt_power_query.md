# Prompt - Génération de script Power Query (M)

Tu es un expert Power BI et Power Query.

## Contexte

- Source : `{source_type}`
- Serveur / base / fichier : `{source_location}`
- Table ou vue : `{table_name}`
- Colonnes a conserver : `{columns}`
- Transformations demandees : `{transformations}`

## Objectif

Produire un script Power Query (M) lisible et maintenable.

## Contraintes

- Ne pas inventer de colonnes ou tables absentes.
- Utiliser des étapes nommees explicitement.
- Limiter la complexité au besoin exprime.
- Ajouter une explication des étapes.

## Sortie attendue

1. Script M complet
2. Explication étape par étape
3. Hypotheses
4. Points de revue humaine

## Exemple Superstore (Phase 9)

```
source_type = SQL Server
source_location = NESNOUSSA\SQLEXPRESS, POC_ETL_IA
table_name = stg_fact_sales (puis stg_dim_customer, stg_dim_product)
columns = conserver toutes sauf masquer batch_id, load_ts en BI si inutiles
transformations = typer dates, pas de jointure en M (faire en modèle)
```
