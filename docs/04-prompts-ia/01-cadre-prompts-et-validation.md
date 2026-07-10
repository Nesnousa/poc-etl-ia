# Phase 6 - Cadre de prompts et validation humaine

## Principe

L'IA ne produit pas un livrable final autonome. Elle produit une proposition technique que le developpeur relit, corrige et valide. Pour que cette assistance soit professionnelle, chaque prompt doit imposer un cadre d'entree, de sortie et de verification.

## Structure standard d'un prompt

Chaque prompt doit contenir :

1. le role attendu de l'IA
2. le contexte technique
3. les donnees d'entree minimales
4. le format exact de sortie
5. les contraintes a respecter
6. les points de vigilance
7. la consigne de ne pas inventer d'information

## Regles de validation humaine

Avant acceptation d'un artefact genere, verifier :

- la coherence fonctionnelle
- la qualite syntaxique
- la conformite aux conventions
- la couverture des logs et erreurs
- la presence de controles qualite
- la lisibilite et la maintenabilite

## Critere d'acceptation

Un artefact IA est accepte s'il est :

- correct sur le plan technique
- comprehensible par un developpeur
- modifiable sans dependre de l'IA
- aligne avec les standards du POC

## Gouvernance

- Toujours conserver le prompt source et la sortie generee.
- Journaliser les corrections manuelles significatives.
- Identifier les cas ou l'IA produit des erreurs recurrentes.
- Mettre a jour les prompts a partir des retours d'usage.
