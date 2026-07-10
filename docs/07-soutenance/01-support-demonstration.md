# Phase 13 - Support de demonstration et soutenance

## Message cle

Ce POC montre comment l'IA peut accelerer la production de composants ETL et BI reutilisables, a condition d'etre encadree par des standards, des prompts structures et une validation humaine systematique.

## Deroule de demonstration recommande (15 a 20 minutes)

### 1. Contexte (2 min)

- probleme des taches repetitives en Data Engineering et BI
- objectif du POC
- perimetre retenu

### 2. Architecture (3 min)

- bibliotheque de templates
- couche de prompts IA
- validation humaine
- extension Power BI
- role potentiel de MCP

### 3. Demo ETL (5 min)

- cas client source vers staging
- generation / reutilisation des templates SQL
- controles qualite
- logging

### 4. Demo Power BI (4 min)

- generation d'une mesure DAX
- generation d'un script Power Query
- explication automatique

### 5. Comparaison et limites (3 min)

- gain de temps observe
- corrections necessaires
- cas ou l'IA est fragile

### 6. Perspectives (2 min)

- industrialisation
- gouvernance
- prochaines etapes

## Points a defendre

- pourquoi SSIS et SQL Server
- pourquoi ne pas automatiser sans validation
- pourquoi separer templates et prompts
- pourquoi MCP seulement sur certains cas
- comment mesurer objectivement les gains

## Limites a assumer

- le POC n'est pas un produit industriel
- les resultats dependent de la qualite des prompts
- l'IA peut inventer des hypotheses si le contexte est incomplet
- la demonstration repose sur des cas d'etude limites mais representatifs

## Questions probables de l'encadrant

1. Pourquoi l'IA ne remplace-t-elle pas le developpeur ?
2. Comment garantissez-vous la qualite des livrables ?
3. Ou MCP apporte-t-il une vraie valeur ?
4. Quels gains avez-vous mesures ?
5. Comment industrialiser ce POC ?
