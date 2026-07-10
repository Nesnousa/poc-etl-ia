# Phase 2 et 3 - Etude SSIS et taches repetitives

## Role de SSIS dans le POC

SSIS permet de construire des flux ETL packages autour de sources, transformations, controles et chargements. Dans un contexte entreprise, son interet principal est la structuration de traitements repetables, parametrables et supervisables.

Le POC ne cherche pas a couvrir tout SSIS, mais a identifier les patterns les plus repetitifs, ceux pour lesquels une assistance IA est utile et safe.

## Composants SSIS a cibler

### Control Flow

- `Execute SQL Task`
- `Data Flow Task`
- `Foreach Loop Container`
- `Sequence Container`
- `Script Task` uniquement si justifie

### Data Flow

- Source OLE DB / Flat File
- Derived Column
- Data Conversion
- Lookup
- Conditional Split
- Aggregate
- OLE DB Destination

## Typologie de flux ETL a standardiser

### Type 1. Source vers staging

Pattern tres frequent :
- lecture source
- controles de base
- insertion en staging
- journalisation du lot

### Type 2. Staging vers integration

Pattern frequent :
- validation metier
- dedoublonnage
- lookup de references
- chargement cible

### Type 3. Controle qualite

Pattern frequent :
- comptage avant / apres
- verification des nulls
- verification des cles orphelines
- verification des doublons

### Type 4. Chargement avec gestion d'erreur

Pattern frequent :
- bloc principal
- capture des erreurs
- ecriture dans une table de logs
- statut de fin de lot

## Taches repetitives a forte valeur pour l'IA

| Tache | Valeur | Risque | Niveau de priorite |
| --- | --- | --- | --- |
| Generer un squelette de package SSIS | Elevee | Moyen | Haute |
| Generer un script SQL de staging | Elevee | Faible | Haute |
| Generer un script de controles qualite | Elevee | Faible | Haute |
| Generer la structure de logging | Elevee | Faible | Haute |
| Generer la documentation technique | Elevee | Faible | Haute |
| Generer des regles de validation metier | Moyenne | Moyen | Moyenne |
| Proposer des optimisations de flux | Moyenne | Moyen a fort | Moyenne |

## Taches moins adaptees a l'automatisation assistee

- Optimisation fine de performances sans contexte d'execution
- Choix d'indexation definitive sans statistiques ni volumetrie
- Diagnostic certain d'un echec SSIS sans logs reels
- Regles metier implicites non formalisees

## Bonnes pratiques retenues

- Separer `staging`, `integration` et `reporting`.
- Centraliser le logging dans des tables dediees.
- Parametrer les flux plutot que dupliquer les packages.
- Nommer les composants selon une convention stable.
- Rendre explicites les preconditions, postconditions et erreurs attendues.
- Conserver la logique metier critique dans des artefacts relisibles et revisables.

## Conclusion

Le POC doit cibler prioritairement les patterns repetitifs et bien formalises : `source-to-staging`, `controle qualite`, `chargement avec logging`, puis documentation. Ce sont les cas ou l'IA peut apporter un gain rapide tout en restant sous controle du developpeur.
