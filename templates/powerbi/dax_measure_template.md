# Template générique — Mesure DAX (Power BI)

## Objectif

Créer une mesure DAX réutilisable sur n'importe quel modèle Power BI, à partir d'un besoin exprimé en langage naturel.

## Comment l'utiliser

1. Remplacer les variables `{...}` par votre contexte.
2. Choisir le patron correspondant au type de calcul (total, filtré, ratio, cumul temporel).
3. Toujours nommer la mesure de façon explicite et l'accompagner d'une courte explication.

Variables à remplacer :

- `{table_faits}` → table de faits, ex. `FactSales`
- `{colonne}` → colonne à agréger, ex. `SalesAmount`
- `{table_dates}` → table de dates, ex. `DimDate`
- `{colonne_filtre}` → colonne servant de filtre, ex. `Region`

## Patrons réutilisables

### 1. Agrégation simple

```DAX
Total {colonne} :=
SUM ( '{table_faits}'[{colonne}] )
```

### 2. Agrégation avec filtre

```DAX
{colonne} filtré :=
CALCULATE (
    SUM ( '{table_faits}'[{colonne}] ),
    '{table_faits}'[{colonne_filtre}] = "Valeur"
)
```

### 3. Ratio / pourcentage

```DAX
% {colonne} :=
DIVIDE (
    SUM ( '{table_faits}'[{colonne}] ),
    CALCULATE ( SUM ( '{table_faits}'[{colonne}] ), ALL ( '{table_faits}' ) )
)
```

### 4. Cumul temporel (Year To Date)

```DAX
{colonne} YTD :=
TOTALYTD (
    SUM ( '{table_faits}'[{colonne}] ),
    '{table_dates}'[Date]
)
```

## Règles de qualité (à respecter)

- Nom de mesure explicite (compréhensible par le métier).
- Gestion claire du contexte de filtre (`CALCULATE`, `ALL`, `FILTER`).
- Utiliser `DIVIDE` plutôt que `/` (gère la division par zéro).
- Éviter la complexité inutile ; commenter la logique métier.
- Toujours associer une explication textuelle à la mesure.
