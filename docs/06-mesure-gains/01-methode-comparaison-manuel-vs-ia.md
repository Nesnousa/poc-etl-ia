# Phase 8 et 12 - Mesure des gains

## Objectif

Comparer un developpement manuel et un developpement assiste par l'IA sur des cas identiques.

## Indicateurs

### Indicateurs quantitatifs

- temps total de production
- temps de correction apres generation IA
- nombre d'iterations de prompt
- nombre d'erreurs detectees a la revue

### Indicateurs qualitatifs

- lisibilite du livrable
- conformite aux standards
- reutilisabilite
- confiance du developpeur dans le resultat

## Protocole de comparaison

1. Definir un cas d'etude.
2. Produire l'artefact manuellement.
3. Produire l'artefact avec assistance IA.
4. Mesurer le temps passe dans chaque approche.
5. Evaluer les corrections necessaires.
6. Comparer le resultat final.

## Exemple de grille

| Cas | Approche | Temps initial | Temps correction | Temps total | Commentaire |
| --- | --- | --- | --- | --- | --- |
| Staging SQL | Manuel | 45 min | 0 min | 45 min | Construction complete manuelle |
| Staging SQL | IA assistee | 10 min | 12 min | 22 min | Gain net, mais revue necessaire |
| DAX simple | Manuel | 20 min | 0 min | 20 min | Bonne maitrise requise |
| DAX simple | IA assistee | 5 min | 6 min | 11 min | Gain sur le premier jet |

## Menaces a la validite

- Niveau de maitrise du developpeur
- Familiarite avec le cas d'etude
- Qualite du prompt
- Complexite reelle du besoin

## Lecture attendue

Le POC ne doit pas seulement montrer un gain de temps. Il doit montrer dans quels cas le gain est robuste, dans quels cas l'IA reste fragile, et quel niveau de supervision humaine demeure indispensable.
