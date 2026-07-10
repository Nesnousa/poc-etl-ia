# Catalogue des composants ETL et BI

## Composants ETL

| ID | Composant | Type | Description | Fichier |
| --- | --- | --- | --- | --- |
| ETL-01 | Table de staging | SQL | Creation d'une table de staging parametree | `templates/sql/staging_table_template.sql` |
| ETL-02 | Controles qualite | SQL | Volume, nulls, doublons, formats | `templates/quality/data_quality_checks_template.sql` |
| ETL-03 | Framework de logging | SQL | Tables et procedures de logging | `templates/logging/etl_logging_framework.sql` |
| ETL-04 | Package source to staging | SSIS | Pattern de chargement source vers staging | `templates/ssis/source_to_staging_template.md` |
| ETL-05 | Documentation technique | Doc | Modele de documentation d'un composant | `templates/technical_documentation_template.md` |
| ETL-06 | Setup Superstore | SQL | Tables landing, staging, rejets, vues SSIS | `samples/sqlserver/cas_etude_superstore_setup.sql` |
| ETL-07 | Ingest Kaggle Python | Python | Chargement CSV vers `raw_superstore` | `samples/python/ingest_superstore_to_sql.py` (7B-2) |
| ETL-08 | Package dim client | SSIS | Dedoublonnage, nettoyage, rejets | `PKG_DIM_CUSTOMER` (7B-3) |
| ETL-09 | Package dim produit + fait | SSIS | Lookup, margin, rejets | `PKG_DIM_PRODUCT`, `PKG_FACT_SALES` (7B-4) |
| ETL-10 | Controles qualite Superstore | SQL | QC-SS-01 a QC-SS-12, synthese PASS/FAIL | `samples/sqlserver/cas_etude_superstore_quality_checks.sql` (7B-5) |

## Composants Power BI

| ID | Composant | Type | Description | Fichier |
| --- | --- | --- | --- | --- |
| BI-01 | Mesure DAX | DAX | Template de generation de mesure | `templates/powerbi/dax_measure_template.md` |
| BI-02 | Script Power Query | M | Template d'import et transformation | `templates/powerbi/power_query_template.m` |

## Prompts associes

| ID | Cas d'usage | Fichier |
| --- | --- | --- |
| PR-01 | Generation template SSIS (generique) | `prompts/prompt_ssis_template_generation.md` |
| PR-02 | Setup SQL staging (7B-1) | `prompts/prompt_sql_staging_setup.md` |
| PR-03 | Ingest Python CSV (7B-2) | `prompts/prompt_python_ingest.md` |
| PR-04 | Package SSIS dimension (7B-3/4) | `prompts/prompt_ssis_dimension_package.md` |
| PR-05 | Package SSIS fait (7B-4) | `prompts/prompt_ssis_fact_package.md` |
| PR-06 | Controles qualite SQL (7B-5) | `prompts/prompt_sql_quality_checks.md` |
| PR-07 | Modele Power BI (Phase 9) | `prompts/prompt_powerbi_model.md` |
| PR-08 | Generation DAX | `prompts/prompt_powerbi_dax.md` |
| PR-09 | Generation Power Query | `prompts/prompt_power_query.md` |

## Jeux d'exemple

| ID | Description | Fichier |
| --- | --- | --- |
| S-01 | Source client SQL Server | `samples/sqlserver/sample_customer_source.sql` |
| S-02 | Exemples de mesures DAX | `samples/powerbi/sample_dax_measures.md` |
| S-03 | Cas Superstore — cadrage | `docs/05-cas-etude/06-cas-etude-superstore-cadrage.md` |
| S-04 | Cas Superstore — setup SQL | `samples/sqlserver/cas_etude_superstore_setup.sql` |
| S-05 | Cas Superstore — guide Kaggle | `samples/python/README_superstore.md` |
