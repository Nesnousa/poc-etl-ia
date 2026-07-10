# Prompt - Génération de contrôles qualite SQL

Tu es un expert SQL Server charge de produire des contrôles qualite de données.

## Contexte

- Table : `{table_name}`
- Colonnes : `{columns}`
- Cle métier ou technique : `{business_key}`
- Règles métier connues : `{business_rules}`
- Batch id disponible : `{batch_id_available}`

## Objectif

Produire un script SQL Server qui contrôle :

- le volume
- les valeurs nulles sur champs obligatoires
- les doublons
- les formats invalides si l'information est fournie

## Contraintes

- Ne pas inventer de règles métier non fournies.
- Produire du SQL Server lisible et comentable.
- Ajouter des commentaires brefs sur chaque bloc de contrôle.

## Sortie attendue

- script SQL complet avec statut PASS/FAIL par contrôle (tableau synthese)
- explication des contrôles
- hypotheses et limites
- pour chaque FAIL : requête diagnostic (TOP N lignes concernees) + action corrective

## Exemple de variables (cas Superstore 7B-5)

```
table_name = stg_dim_customer, stg_dim_product, stg_fact_sales, raw_superstore
business_key = customer_id, product_id, row_id
business_rules = QC-SS-01 volume raw > 9000; QC-SS-06 orphelins = 0; QC-SS-12 packages SUCCESS
reference_script = samples/sqlserver/cas_etude_superstore_quality_checks.sql
```
