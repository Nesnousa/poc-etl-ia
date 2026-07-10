# Guide Power BI — Cas Superstore (Phase 9)

| Date | 2026-07-02 |
| --- | --- |
| Prerequis | Phase 7B validee (staging charge, QC 12/12 PASS) |
| Outil | Power BI Desktop |
| Source | SQL Server `POC_ETL_IA` sur `NESNOUSSA\SQLEXPRESS` |
| Statut | **A VALIDER** — construction manuelle dans PBI Desktop |

## Objectif

Construire un modele en **etoile** sur les tables staging SSIS :

```
stg_dim_customer ──┐
                   ├── stg_fact_sales
stg_dim_product  ──┘
```

## Fichiers livres

| Fichier | Role |
| --- | --- |
| `samples/powerbi/superstore/superstore_power_query.m` | Scripts M (3 tables) |
| `samples/powerbi/superstore/superstore_dax_measures.md` | Mesures DAX |
| `samples/sqlserver/cas_etude_superstore_validate_powerbi.sql` | Controles croises SQL vs PBI |
| `docs/05-cas-etude/11-guide-powerbi-superstore-phase9.md` | Ce guide |

---

## Etape 1 — Creer le fichier Power BI

1. Ouvrir **Power BI Desktop**
2. **Fichier → Enregistrer sous** → `Superstore_POC.pbix` (dossier projet recommande)

---

## Etape 2 — Importer les 3 tables SQL

### Connexion

1. **Accueil → Obtenir des donnees → SQL Server**
2. Serveur : `NESNOUSSA\SQLEXPRESS` (ou `localhost\SQLEXPRESS`)
3. Base : `POC_ETL_IA`
4. Mode de connectivite : **Importer** (recommande pour le POC)
5. Selectionner les tables :
   - `dbo.stg_fact_sales`
   - `dbo.stg_dim_customer`
   - `dbo.stg_dim_product`

### Power Query — transformations communes (pour chaque table)

Dans l'Editeur Power Query, pour **chaque** table :

1. **Filtrer** `batch_id = 1` (lot ETL valide)
2. **Supprimer** colonnes techniques si inutiles en visuel :
   - `batch_id`, `source_system`, `load_ts`
3. Verifier les types : dates en Date, montants en Nombre decimal

Scripts M de reference : `samples/powerbi/superstore/superstore_power_query.m`

4. **Fermer et appliquer**

---

## Etape 3 — Modele et relations

Ouvrir **Modele** (icone tables liees a gauche).

### Relations a creer

| De | Vers | Cardinalite | Direction filtre |
| --- | --- | --- | --- |
| `stg_fact_sales[customer_id]` | `stg_dim_customer[customer_id]` | Plusieurs → un | Unique de la dimension vers le fait |
| `stg_fact_sales[product_id]` | `stg_dim_product[product_id]` | Plusieurs → un | Unique de la dimension vers le fait |

### Verifications

- Pas de relation ambigue ou circulaire
- `customer_id` et `product_id` non NULL en fait (deja valide en 7B-5)
- Activer **Integrite referentielle** si propose (optionnel en Import)

### Renommoyer (optionnel, lisibilite)

| Table actuelle | Nom affiche suggere |
| --- | --- |
| `stg_fact_sales` | `Fact Sales` |
| `stg_dim_customer` | `Dim Customer` |
| `stg_dim_product` | `Dim Product` |

---

## Etape 4 — Mesures DAX

Dans **Fact Sales** (ou table de mesures dediee), creer les mesures du fichier :

`samples/powerbi/superstore/superstore_dax_measures.md`

Mesures prioritaires :

| Mesure | Usage |
| --- | --- |
| Total Sales | KPI CA |
| Total Profit | KPI profit |
| Margin % | KPI marge |
| # Orders | Nombre de commandes |
| Avg Discount | Remise moyenne |

---

## Etape 5 — Page de demonstration (3 visuels minimum)

### Page « Vue Superstore »

| Visuel | Champs |
| --- | --- |
| **Cartes** (3) | Total Sales, Total Profit, Margin % |
| **Graphique barres** | Axe : `Dim Customer[region]` — Valeur : Total Sales |
| **Graphique barres** | Axe : `Dim Product[category]` — Valeur : Total Profit |
| **Table** (optionnel) | order_id, customer_name, product_name, sales, profit |

### Filtres recommandes

- Segment client (`Dim Customer[segment]`)
- Annee commande (`Fact Sales[order_date]` → hierarchie annee)

---

## Etape 6 — Validation (obligatoire)

### Dans Power BI

Comparer les totaux avec SQL :

| Indicateur | Attendu (~) |
| --- | --- |
| Total Sales | ~2 297 201 USD (somme des sales) |
| Lignes fact | 9 994 |
| Margin % globale | coherente avec `SUM(profit)/SUM(sales)` |

### Dans SSMS

Executer :

```sql
:r samples/sqlserver/cas_etude_superstore_validate_powerbi.sql
```

Les totaux SQL doivent **correspondre** aux cartes Power BI (ecart = 0 ou arrondi affichage).

---

## Depannage

| Probleme | Solution |
| --- | --- |
| Connexion SQL refusee | Verifier SQL Server demarre, base `POC_ETL_IA`, auth Windows |
| Totaux PBI ≠ SQL | Verifier filtre `batch_id = 1`, relations actives |
| Region vide en visuel | Relation customer_id inactive ou mauvaise direction filtre |
| Gateway / Express | Import local OK ; publication cloud necessite passerelle |

---

## Criteres de validation Phase 9

- [ ] 3 tables importees depuis staging
- [ ] 2 relations en etoile correctes
- [ ] 5 mesures DAX fonctionnelles
- [ ] 3+ visuels sur une page demo
- [ ] Totaux PBI = totaux SQL (validate script)
- [ ] Fichier `.pbix` sauvegarde

## Prochaine etape

Validation humaine → doc `12-validation-powerbi-superstore-phase9.md` (apres tes captures / chiffres).
