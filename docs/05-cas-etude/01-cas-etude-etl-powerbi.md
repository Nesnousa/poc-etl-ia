# Phase 7 — Cas d'étude

## Cas d'étude 1 — ETL source vers staging

### Scénario

Une source clients doit être chargée quotidiennement vers SQL Server pour alimenter des traitements de qualité puis des usages analytiques.

### Entrées

- Fichier ou table source avec données clients
- Table cible `stg_sales_customer`
- Besoin de journalisation (logging) et de contrôles de base

### Livrables attendus

- Template de package SSIS
- Script de création de la zone de staging
- Contrôles qualité
- Documentation technique

### Mesures à observer

- Temps de production manuel
- Temps avec assistance IA
- Nombre de corrections manuelles

## Cas d'étude 2 — ETL avec contrôle qualité et gestion d'erreur

### Scénario

Un flux de chargement doit rejeter les lignes incohérentes, journaliser les erreurs et produire un statut de lot.

### Livrables attendus

- Script de journalisation
- Gestion d'erreur standardisée
- Contrôles de doublons et de champs obligatoires

## Cas d'étude 3 — Génération de mesure DAX

### Scénario

Un utilisateur demande une mesure de ventes et son explication.

### Livrables attendus

- Mesure DAX lisible
- Explication fonctionnelle
- Points de vigilance sur le contexte de filtre

## Cas d'étude 4 — Génération de script Power Query

### Scénario

Une table SQL Server doit être importée et préparée dans Power BI avec quelques renommages et sélections de colonnes.

### Livrables attendus

- Script M
- Explication des étapes
- Limites et hypothèses

## Conclusion

Ces cas couvrent les usages les plus défendables du POC : génération structurée, documentation, qualité et accélération du travail sur des schémas répétitifs.

> Le cas d'étude Superstore (voir `06-cas-etude-superstore-cadrage.md`) reprend l'intégralité de ces principes sur un jeu de données réel d'environ 10 000 lignes, de l'ingestion à la restitution Power BI.
