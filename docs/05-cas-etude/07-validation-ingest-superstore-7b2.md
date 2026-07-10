# Validation ingest Superstore - Phase 7B-2

| Date | 2026-07-02 |
| --- | --- |
| Script | `samples/python/ingest_superstore_to_sql.py` |
| Source | `samples/data/superstore/Sample - Superstore.csv` |
| Statut | VALIDE |

## Resultats observes

| Controle | Attendu (ordre de grandeur) | Observe | Statut |
| --- | --- | --- | --- |
| Lignes raw_superstore | ~9 900 | 9 994 | OK |
| Clients distincts | ~790 | 793 | OK |
| Produits distincts | ~1 860 | 1 862 | OK |
| Periode commandes | 2014-2017 | 2014-01-03 -> 2017-12-30 | OK |
| ingest_batch_id | 1 | 1 | OK |

## Commande executee

```bash
pip install -r requirements.txt
python samples/python/ingest_superstore_to_sql.py --download
```

## Verification SQL

```sql
USE POC_ETL_IA;
SELECT COUNT(*) FROM raw_superstore;
SELECT COUNT(DISTINCT customer_id) FROM raw_superstore;
SELECT TOP 3 customer_id, customer_name, sales FROM raw_superstore;
```

## Conclusion

La couche landing est alimentee. Prochaine etape : **7B-3** package SSIS `PKG_DIM_CUSTOMER`.
