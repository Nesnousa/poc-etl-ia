# Superstore — Instructions Kaggle (Phase 7B-2)

## Dataset recommande

**Superstore Sales** — fichier type Tableau : `Sample - Superstore.csv`

Sources possibles :

| Source | Lien | Remarque |
| --- | --- | --- |
| Kaggle (forecasting) | https://www.kaggle.com/datasets/vizeno/shop-store-sales-forecasting | Verifier le nom exact du CSV |
| Tableau Sample Data | https://community.tableau.com/s/question/0D54T00000CWeX8SAL/sample-superstore-data | Fichier de reference industrie |
| GitHub mirrors | Rechercher `Sample - Superstore.csv` | Pour tests hors Kaggle |

## Colonnes attendues (CSV)

Le script Python 7B-2 attend ces en-tetes (avec espaces) :

```
Row ID, Order ID, Order Date, Ship Date, Ship Mode,
Customer ID, Customer Name, Segment, Country, City, State,
Postal Code, Region, Product ID, Category, Sub-Category,
Product Name, Sales, Quantity, Discount, Profit
```

Mapping vers SQL : voir `docs/05-cas-etude/06-cas-etude-superstore-cadrage.md`

## Etape 1 — Telecharger le fichier

### Option A — Manuel (recommande pour le POC)

1. Creer un compte Kaggle si necessaire
2. Telecharger le dataset
3. Placer le CSV dans :

```
samples/data/superstore/Sample - Superstore.csv
```

### Option B — API Kaggle

```bash
pip install kaggle
# Configurer ~/.kaggle/kaggle.json avec votre token API
kaggle datasets download -d vizeno/shop-store-sales-forecasting -p samples/data/superstore
```

Decompresser le ZIP et renommer le fichier si besoin.

## Etape 2 — Prerequis SQL

Executer dans SSMS **avant** l'ingest :

```
samples/sqlserver/cas_etude_superstore_setup.sql
```

## Etape 3 — Ingest Python (7B-2)

Script : `samples/python/ingest_superstore_to_sql.py`

```bash
pip install -r requirements.txt
python samples/python/ingest_superstore_to_sql.py --download
```

Ou si vous avez deja le CSV Kaggle :

```bash
python samples/python/ingest_superstore_to_sql.py --csv "samples/data/superstore/Sample - Superstore.csv"
```

Parametres par defaut :

| Parametre | Valeur |
| --- | --- |
| Serveur | `localhost\SQLEXPRESS` |
| Base | `POC_ETL_IA` |
| Table | `raw_superstore` |
| batch_id | 1 |

## Etape 4 — Verifier le chargement

```sql
USE POC_ETL_IA;

SELECT COUNT(*) AS raw_rows FROM raw_superstore;
SELECT COUNT(DISTINCT customer_id) AS customers FROM raw_superstore;
SELECT COUNT(DISTINCT product_id) AS products FROM raw_superstore;
SELECT TOP 5 * FROM raw_superstore;
```

Attendu (ordre de grandeur) :

| Metrique | Valeur indicative |
| --- | --- |
| raw_rows | ~9 900 |
| customers | ~790 |
| products | ~1 860 |

## Dépannage

| Probleme | Solution |
| --- | --- |
| Colonnes differentes | Adapter le mapping dans le script Python |
| Dates invalides | Format US `M/D/YYYY` — conversion dans pandas |
| Connexion SQL | Meme config que SSIS : `Trust Server Certificate=yes` |
| Encodage CSV | Essayer `encoding='utf-8'` ou `latin-1` |

## Suite

Apres ingest valide → **7B-3** : package SSIS `PKG_DIM_CUSTOMER`.
