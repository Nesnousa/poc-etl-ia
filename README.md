# POC IA pour ETL et Power BI

Ce repository contient un Proof of Concept visant a accelerer la production de composants Data Engineering et BI grace a l'assistance IA, tout en conservant une validation humaine systematique.

## Objectif

Le POC couvre deux axes en parallele :

- un noyau `SQL Server + SSIS` pour la generation de composants ETL reutilisables
- un axe `Power BI` pour l'assistance a la generation, l'explication et l'optimisation d'artefacts BI

## Structure

- `docs/01-cadrage` : besoin metier, objectifs, perimetre et criteres de succes
- `docs/02-ssis` : cadrage SSIS et taches repetitives
- `docs/03-bibliotheque-etl` : catalogue de composants et standards
- `docs/04-prompts-ia` : prompts, gouvernance et revue humaine
- `docs/05-cas-etude` : scenarios de test ETL et Power BI
- `docs/06-mesure-gains` : methode de mesure et comparaison manuel vs IA
- `docs/07-soutenance` : support de demonstration, soutenance et rapport
- `templates/` : templates reutilisables ETL, SQL, qualite, logging et Power BI
- `prompts/` : prompts operationnels par cas d'usage
- `samples/` : jeux d'exemples pour la demonstration
- `app/` : mini interface Streamlit de demonstration
- `ssis/` : projet SSIS `POC_ETL_IA_SSIS` avec le package Cas d'etude 1

## Principe directeur

L'IA assiste le developpeur sur les taches repetitives, standardisables et documentables :

- generation de templates
- generation de scripts SQL
- controles qualite
- logging et gestion des erreurs
- documentation technique
- generation de DAX et de Power Query
- analyse et optimisation

La validation finale reste toujours humaine.

## Demarrage rapide

```bash
pip install -r requirements.txt
streamlit run app/streamlit_demo.py
```

## Prochaine etape recommandee

Valider ensemble la Phase 1 (`docs/01-cadrage/01-besoin-metier.md`), puis lancer les tests reels sur le cas client avec SQL Server, SSIS et Power BI Desktop.
