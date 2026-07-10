# Prompt - Génération de template SSIS (generique)

Tu es un expert SSIS, SQL Server et Data Engineering.

> **Note POC** : pour une dimension ou un fait Superstore, preferer les prompts specialises :
> - `prompt_ssis_dimension_package.md` (7B-3 / 7B-4 produit)
> - `prompt_ssis_fact_package.md` (7B-4 ventes)

## Contexte

- Source : `{source_type}`
- Cible : `{target_table}`
- Pattern ETL : `{etl_pattern}` (ex. `source_to_staging`, `dimension`, `fact`)
- Colonnes principales : `{columns}`
- Règles de qualite : `{quality_rules}`
- Besoins de logging : `{logging_requirements}`

## Contraintes

- Ne pas inventer de metadonnees absentes.
- Utiliser des composants SSIS standards si possible.
- Preferer transformations SQL en source si XML SSIS fragile (Derived Column, Lookup).
- Inclure logging (`etl_run_log`, `etl_reject_log`) et gestion d'erreur.
- Produire une sortie lisible par un developpeur.

## Sortie attendue

1. Description du package
2. Structure Control Flow
3. Structure Data Flow
4. Paramètres et variables SSIS
5. Gestion d'erreur et rejets
6. Scripts reset / validation SQL
7. Points de revue humaine (Visual Studio)
