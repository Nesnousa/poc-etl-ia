# Validation SSIS Superstore - Phase 7B-4 (PKG_DIM_PRODUCT + PKG_FACT_SALES)

| Date | 2026-07-02 |
| --- | --- |
| Packages | `PKG_DIM_PRODUCT`, `PKG_FACT_SALES` |
| Generateurs | `ssis/superstore/generate_ssis_dim_product.py`, `generate_ssis_fact_sales.py` |
| Statut | **VALIDE** — execution Visual Studio 2026-07-02 |

## Objectif

Completer la couche staging Superstore apres `PKG_DIM_CUSTOMER` (7B-3) :

1. **Dimension produit** : `vw_extract_superstore_products` → `stg_dim_product` (~1 862 lignes)
2. **Fait ventes** : `vw_extract_superstore_sales` → `stg_fact_sales` (~9 994 lignes), avec lookup dimensions et `margin_pct`

## Fichiers livres

| Fichier | Role |
| --- | --- |
| `ssis/superstore/ssis_package_builder.py` | Builder SSIS reutilisable (pattern 7B-3) |
| `ssis/superstore/generate_ssis_dim_product.py` | Genere `PKG_DIM_PRODUCT.dtsx` |
| `ssis/superstore/generate_ssis_fact_sales.py` | Genere `PKG_FACT_SALES.dtsx` |
| `ssis/superstore/run_pkg_dim_product.ps1` | Script terminal produit |
| `ssis/superstore/run_pkg_fact_sales.ps1` | Script terminal fait |
| `ssis/superstore/run_superstore_7b4.ps1` | Enchaine produit puis fait |
| `ssis/POC_ETL_IA_SSIS/PKG_DIM_PRODUCT.dtsx` | Package produit genere |
| `ssis/POC_ETL_IA_SSIS/PKG_FACT_SALES.dtsx` | Package fait genere |
| `samples/sqlserver/cas_etude_superstore_reset_stg_product.sql` | Reset staging produit |
| `samples/sqlserver/cas_etude_superstore_reset_stg_fact.sql` | Reset staging fait |
| `samples/sqlserver/cas_etude_superstore_validate_product_fact.sql` | Controles post-run |

## Architecture (meme pattern que 7B-3)

Les transformations SSIS fragiles (Lookup, Derived Column, Conditional Split) sont **implementees en SQL** dans la requete OLE DB Source et dans `SQL_LogRejects`, comme pour le client.

### PKG_DIM_PRODUCT

```text
SQL_StartRun
  -> SQL_CountSource (produits distincts)
  -> SQL_LogRejects (product_id null ou product_name vide)
  -> DFT_LoadProduct
       OLE DB Source (GROUP BY product_id + filtre valide)
       -> RC_Valid
       -> OLE DB Destination Product (stg_dim_product)
  -> SQL_EndRunSuccess
```

### PKG_FACT_SALES

```text
SQL_StartRun
  -> SQL_CountSource (lignes avec lookup dimensions OK)
  -> SQL_LogRejects (cles manquantes ou absentes des dimensions)
  -> DFT_LoadFactSales
       OLE DB Source (INNER JOIN stg_dim_customer + stg_dim_product + margin_pct)
       -> RC_Valid
       -> OLE DB Destination Fact Sales (stg_fact_sales)
  -> SQL_EndRunSuccess
```

**Prerequis** : `stg_dim_customer` (793 lignes, 7B-3) et `stg_dim_product` charges avant `PKG_FACT_SALES`.

## Commandes terminal

```powershell
# Generer les deux packages
python ssis/superstore/generate_ssis_dim_product.py
python ssis/superstore/generate_ssis_fact_sales.py

# Ou tout-en-un (produit puis fait)
powershell -ExecutionPolicy Bypass -File ssis/superstore/run_superstore_7b4.ps1
```

## Procedure de validation (Visual Studio)

1. Fermer VS sans sauvegarder si un ancien package est ouvert.
2. Executer les generateurs Python (copie auto vers `C:\POC_ETL_IA_SSIS\POC_ETL_IA_SSIS\`).
3. Ouvrir le projet SSIS dans Visual Studio.
4. **PKG_DIM_PRODUCT** :
   - Executer `cas_etude_superstore_reset_stg_product.sql` dans SSMS
   - Start sur `PKG_DIM_PRODUCT.dtsx`
5. **PKG_FACT_SALES** :
   - Verifier `stg_dim_customer` = 793 et `stg_dim_product` = ~1862
   - Executer `cas_etude_superstore_reset_stg_fact.sql`
   - Start sur `PKG_FACT_SALES.dtsx`
6. Executer `cas_etude_superstore_validate_product_fact.sql`

## Resultats observes (validation 2026-07-02)

| Controle | Attendu | Observe | Statut |
| --- | --- | --- | --- |
| `stg_dim_product` | ~1 862 | **1 862** | OK |
| `row_count_in` / `row_count_out` (produit) | ~1 862 | **1 862 / 1 862** (run_id=11) | OK |
| `stg_fact_sales` | ~9 994 | **9 994** | OK |
| `row_count_in` / `row_count_out` (fait) | ~9 994 | **9 994 / 9 994** (run_id=12) | OK |
| `etl_run_log.status` | SUCCESS | **SUCCESS** (2 packages) | OK |
| Rejets produit | 0 | **0** | OK |
| Rejets fait (lookup) | 0 | **0** | OK |
| Cles orphelines client | 0 | **0** | OK |
| Cles orphelines produit | 0 | **0** | OK |
| `stg_dim_customer` (prerequis) | 793 | **793** | OK |

**Note** : `vw_extract_superstore_products` compte **1 894** lignes distinctes ; **1 862** sont chargees car **32** produits ont un `product_name` vide (filtre `HAVING` + rejets = comportement attendu).

Packages executes dans Visual Studio : `PKG_DIM_PRODUCT.dtsx` puis `PKG_FACT_SALES.dtsx` — tous les tasks verts.

## Verification SQL

```sql
:r samples/sqlserver/cas_etude_superstore_validate_product_fact.sql
```

## Notes techniques

- **Lookup** : remplace par `INNER JOIN` sur `stg_dim_customer` et `stg_dim_product` (batch_id = 1) dans la source SQL.
- **margin_pct** : calcule en SQL (`CASE WHEN sales <> 0 THEN profit/sales ELSE NULL END`).
- **Rejets** : `SQL_LogRejects` avec `LEFT JOIN` pour detecter les lignes sans dimension.
- Si `dtexec` echoue avec `0xC000F427` (SQL Express), executer dans Visual Studio comme en 7B-3.
