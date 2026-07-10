# Phase 11 - Demonstration complete du POC

## Enchainement recommande

1. Presenter le besoin metier (`docs/01-cadrage/01-besoin-metier.md`)
2. Montrer la cartographie SSIS et les taches repetitives (`docs/02-ssis/`)
3. Ouvrir le catalogue de composants (`docs/03-bibliotheque-etl/02-catalogue-composants.md`)
4. Executer ou montrer un cas ETL client
5. Montrer les controles qualite et le logging
6. Passer au cas Power BI DAX / M
7. Presenter la comparaison manuel vs IA
8. Conclure sur MCP et les perspectives

## Commandes utiles

```bash
pip install -r requirements.txt
streamlit run app/streamlit_demo.py
```

## Artefacts a montrer en live

- `templates/sql/staging_table_template.sql`
- `templates/quality/data_quality_checks_template.sql`
- `templates/logging/etl_logging_framework.sql`
- `prompts/prompt_ssis_template_generation.md`
- `prompts/prompt_powerbi_dax.md`
- `samples/sqlserver/sample_customer_source.sql`

## Message de cloture

Le POC demontre qu'une assistance IA bien cadree peut reduire le temps de production sur des taches repetitives, mais que la qualite finale depend toujours des standards, des prompts et de la validation humaine.
