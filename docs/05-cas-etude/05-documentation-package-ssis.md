# Documentation technique - PKG_SRC_CUSTOMER_STG_SALES_CUSTOMER

## Identification

| Element | Valeur |
| --- | --- |
| Nom | PKG_SRC_CUSTOMER_STG_SALES_CUSTOMER |
| Type | SSIS Package |
| Pattern | Source to Staging |
| Version | 1.0 |
| Auteur | nesrine |
| Date | 2026-07-02 |

## Objectif

Charger les donnees clients depuis `src_customer` vers `stg_sales_customer` avec journalisation ETL et gestion d'erreur.

## Entrees

- Table source : `dbo.src_customer`
- Parametres : batch_id, source_system, package_name, created_by

## Sorties

- Table cible : `dbo.stg_sales_customer`
- Logs : `etl_run_log`, `etl_error_log`

## Control Flow

1. **SQL_StartRun** : demarre un run via `usp_log_etl_run_start`
2. **SQL_CountSource** : compte les lignes source
3. **DFT_LoadStaging** : charge la staging
4. **SQL_EndRunSuccess** : cloture le run en SUCCESS

## Data Flow

1. **OLE DB Source** : lecture `src_customer`
2. **DER_AddMetadata** : ajout batch_id, source_system, source_extract_ts, load_ts
3. **Row Count** : alimente `User::RowCountOut`
4. **OLE DB Destination** : ecriture `stg_sales_customer`

## Gestion des erreurs

- Handler `OnError` au niveau package
- Tache `SQL_LogError` insere dans `etl_error_log`

## Procedure de test

1. Executer le script de reset SQL
2. Lancer le package (F5)
3. Verifier staging et logs
4. Executer les controles qualite

## Fichier projet

`ssis/POC_ETL_IA_SSIS/PKG_SRC_CUSTOMER_STG_SALES_CUSTOMER.dtsx`
