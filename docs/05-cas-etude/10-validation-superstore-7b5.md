# Validation Superstore - Phase 7B-5 (Controles qualite finaux)

| Date | 2026-07-02 |
| --- | --- |
| Script | `samples/sqlserver/cas_etude_superstore_quality_checks.sql` |
| Interface | `app/streamlit_demo.py` (onglet Superstore QC) |
| Statut | **VALIDE** — 12/12 controles PASS |

## Objectif

Clore la phase **7B** du cas Superstore en validant l'integrite du pipeline ETL complet :

```
CSV Kaggle → Python ingest → raw_superstore
  → PKG_DIM_CUSTOMER → stg_dim_customer
  → PKG_DIM_PRODUCT  → stg_dim_product
  → PKG_FACT_SALES   → stg_fact_sales
  → Controles QC-SS  → pret Power BI (Phase 9)
```

## Fichiers livres

| Fichier | Role |
| --- | --- |
| `samples/sqlserver/cas_etude_superstore_quality_checks.sql` | 12 controles PASS/FAIL/WARN |
| `ssis/superstore/run_superstore_7b5.ps1` | Execution terminal des QC |
| `app/streamlit_demo.py` | Onglet **Superstore QC** (connexion live SQL) |
| `docs/05-cas-etude/10-validation-superstore-7b5.md` | Ce document |

## Resultats observes (2026-07-02)

| ID | Controle | Observe | Seuil | Statut |
| --- | --- | --- | --- | --- |
| QC-SS-01 | Volume raw | **9 994** | > 9 000 | PASS |
| QC-SS-02 | Clients distincts staging | **793** | > 700 | PASS |
| QC-SS-03 | Produits distincts staging | **1 862** | > 1 800 | PASS |
| QC-SS-04 | customer_id NULL staging | **0** | = 0 | PASS |
| QC-SS-05 | product_id NULL staging | **0** | = 0 | PASS |
| QC-SS-06 | Fait sans dimension | **0** | = 0 | PASS |
| QC-SS-07 | Ventes negatives | **0** | = 0 | PASS |
| QC-SS-08 | Discount hors [0, 1] | **0** | = 0 | PASS |
| QC-SS-09 | Doublons customer_id | **0** | = 0 | PASS |
| QC-SS-10 | Doublons product_id | **0** | = 0 | PASS |
| QC-SS-11 | Reconciliation fait / raw | **9 994 / 9 994** | = raw | PASS |
| QC-SS-12 | Packages SSIS SUCCESS | **3 / 3** | = 3 | PASS |

**Synthese** : 12 PASS, 0 FAIL, 0 WARN.

## Volumes par couche

| Couche | Lignes |
| --- | --- |
| `raw_superstore` | 9 994 |
| `stg_dim_customer` | 793 |
| `stg_dim_product` | 1 862 |
| `stg_fact_sales` | 9 994 |
| `etl_reject_log` (superstore) | 0 |

## Runs ETL retenus

| run_id | Package | in | out | Statut |
| --- | --- | --- | --- | --- |
| 10 | PKG_DIM_CUSTOMER | 793 | 793 | SUCCESS |
| 11 | PKG_DIM_PRODUCT | 1 862 | 1 862 | SUCCESS |
| 12 | PKG_FACT_SALES | 9 994 | 9 994 | SUCCESS |

## Verification regle margin_pct

Echantillon : `margin_pct` = `profit / sales` quand `sales <> 0` (ex. row_id=1 : 41.91/261.96 = 0.16). OK.

## Commandes

```powershell
# Terminal
powershell -ExecutionPolicy Bypass -File ssis/superstore/run_superstore_7b5.ps1

# SSMS
:r samples/sqlserver/cas_etude_superstore_quality_checks.sql

# Streamlit
streamlit run app/streamlit_demo.py
# → onglet "Superstore QC" → bouton "Executer les controles QC-SS"
```

## Bilan phase 7B

| Etape | Statut |
| --- | --- |
| 7B-1 Setup SQL | VALIDE |
| 7B-2 Ingest Python | VALIDE |
| 7B-3 PKG_DIM_CUSTOMER | VALIDE |
| 7B-4 PKG_DIM_PRODUCT + PKG_FACT_SALES | VALIDE |
| 7B-5 Controles qualite | **VALIDE** |

## Prochaine etape

**Phase 9** : modele Power BI sur `stg_dim_customer`, `stg_dim_product`, `stg_fact_sales`.
