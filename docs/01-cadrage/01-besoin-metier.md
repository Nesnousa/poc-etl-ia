# Phase 1 - Besoin metier

## Contexte

Dans de nombreux projets Data, une part importante du temps est consacree a des taches repetitives : creation de flux ETL proches les uns des autres, generation de scripts SQL de staging, mise en place de controles qualite, logging, gestion des erreurs et documentation technique. Les equipes BI rencontrent le meme phenomene avec DAX, Power Query, l'explication des mesures et l'analyse de modeles.

Le POC propose de structurer une assistance IA pour accelerer ces travaux sans supprimer le role du developpeur. L'objectif n'est pas l'automatisation totale, mais la reduction du temps de production sur des artefacts repetitifs et standardisables.

## Probleme actuel

- Les composants ETL sont souvent reconstruits plusieurs fois avec des variantes mineures.
- La documentation est produite tardivement ou de maniere inegale.
- Les controles qualite et le logging ne sont pas toujours homogenes.
- Les developpeurs BI passent du temps sur des formules DAX et scripts M repetitifs.
- Les gains de l'IA sont rarement encadres par une methode de validation claire.

## Objectifs du POC

- Standardiser la production de composants ETL reutilisables.
- Utiliser l'IA pour proposer plus rapidement des artefacts techniques de qualite.
- Encadrer l'usage de l'IA par des prompts, des regles de revue et des criteres d'acceptation.
- Etudier des usages concrets cote Power BI.
- Mesurer le gain entre un developpement manuel et un developpement assiste.

## Utilisateurs cibles

- Developpeur Data / ETL
- Ingenieur BI
- Lead Data / architecte BI
- Stagiaire ou junior encadre par un referentiel de bonnes pratiques

## Contraintes

- Validation humaine obligatoire avant integration.
- Solutions realistes pour SQL Server, SSIS, Visual Studio et Power BI Desktop.
- POC demonstrable dans un cadre de stage.
- Peu ou pas de dependances lourdes a industrialiser.
- Traçabilite des decisions et reproductibilite des tests.

## Perimetre du POC

### Dans le POC

- Templates SSIS
- Scripts SQL Server
- Controles qualite
- Logging et gestion d'erreurs
- Documentation technique
- Cas d'usage Power BI sur DAX, M et documentation
- Evaluation ciblee de MCP

### Hors POC

- Deploiement industriel complet CI/CD
- Catalogue d'entreprise complet de metadonnees
- Auto-correction sans validation humaine
- Couverture exhaustive de tous les composants SSIS et Power BI

## Criteres de succes

- Les artefacts generes sont exploitables avec des corrections limitees.
- Le temps de production est reduit sur les cas d'etude retenus.
- Les templates produits respectent des standards explicites.
- Les limites de l'IA sont clairement identifiees.
- La demarche est defendable techniquement devant un encadrant.
