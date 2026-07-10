# Validation SSIS Superstore - Phase 7B-3 (PKG_DIM_CUSTOMER)

| Date | 2026-07-02 |
| --- | --- |
| Package | `PKG_DIM_CUSTOMER` |
| Generateur | `ssis/superstore/generate_ssis_dim_customer.py` |
| Statut | **VALIDE** — execution Visual Studio 2026-07-02 |

## Objectif

Charger la dimension client Superstore depuis `vw_extract_superstore_customers` vers `stg_dim_customer`, avec :

- dedoublonnage par `customer_id` (requete SQL source + `GROUP BY`)
- nettoyage `customer_name_clean` (Derived Column SSIS)
- metadonnees ETL (`batch_id`, `source_system`, `is_active`, `load_ts`)
- journalisation `etl_run_log` + rejets `etl_reject_log`
- comptage lignes (`RowCountIn`, `RowCountOut`, `RowCountReject`)

## Fichiers livres

| Fichier | Role |
| --- | --- |
| `ssis/superstore/generate_ssis_dim_customer.py` | Genere `PKG_DIM_CUSTOMER.dtsx` |
| `ssis/superstore/run_pkg_dim_customer.ps1` | Script terminal tout-en-un |
| `ssis/POC_ETL_IA_SSIS/PKG_DIM_CUSTOMER.dtsx` | Package SSIS genere |
| `samples/sqlserver/cas_etude_superstore_reset_stg_customer.sql` | Reset staging avant run |
| `samples/sqlserver/cas_etude_superstore_validate_customer.sql` | Controles post-run |

## Flux du package

```text
SQL_StartRun
  -> SQL_CountSource (clients distincts)
  -> SQL_LogRejects (invalides -> etl_reject_log)
  -> DFT_LoadCustomer
       OLE DB Source (SQL dedupe + filtre valide)
       -> DER_CleanAndMeta
       -> RC_Valid
       -> OLE DB Destination (stg_dim_customer)
  -> SQL_EndRunSuccess
```

## Commandes terminal

```powershell
# Depuis la racine du projet
python ssis/superstore/generate_ssis_dim_customer.py

powershell -ExecutionPolicy Bypass -File ssis/superstore/run_pkg_dim_customer.ps1
```

Le script :

1. regenere le `.dtsx`
2. reset `stg_dim_customer`
3. lance `dtexec` si disponible
4. affiche les comptages SQL

## Resultats observes (validation 2026-07-02)

| Controle | Attendu | Observe | Statut |
| --- | --- | --- | --- |
| `stg_dim_customer` | ~793 | **793** | OK |
| Clients distincts | ~793 | **793** | OK |
| `row_count_in` / `row_count_out` | ~793 | **793 / 793** | OK |
| `etl_run_log.status` | SUCCESS | **SUCCESS** (run_id=10) | OK |
| `reject_rows` | 0 | **0** | OK |
| `source_system` | KAGGLE_SUPERSTORE | KAGGLE_SUPERSTORE | OK |
| QC-SS-04 | 0 null | 0 | OK |

Package execute dans Visual Studio : `PKG_DIM_CUSTOMER.dtsx` — `OLE DB Destination Customer` a ecrit **793 rows**.

## Verification SQL

```sql
-- Fichier complet
:r samples/sqlserver/cas_etude_superstore_validate_customer.sql
```

Ou manuellement :

```sql
USE POC_ETL_IA;
SELECT COUNT(*) FROM stg_dim_customer;
SELECT TOP 5 customer_id, customer_name_clean, segment FROM stg_dim_customer;
SELECT * FROM etl_run_log WHERE package_name = 'PKG_DIM_CUSTOMER' ORDER BY run_id DESC;
```

## Note importante — execution dtexec

Sur **SQL Server Express** sans composant **Integration Services** installe, `dtexec` peut charger le package mais echouer au Data Flow avec :

`0xC000F427 — install Standard Edition (64-bit) of Integration Services or higher`

Dans ce cas (comme pour le Cas 1) :

1. Ouvrir `ssis/POC_ETL_IA_SSIS.sln` dans Visual Studio
2. Ajouter / ouvrir `PKG_DIM_CUSTOMER.dtsx`
3. Executer le package (F5)
4. Valider avec le script SQL ci-dessus

Le generateur terminal reste la methode de production du package ; l'execution peut se faire via VS selon l'environnement.

## Prochaine etape

**7B-4** : `PKG_DIM_PRODUCT` + `PKG_FACT_SALES` (meme approche generateur + script run).
