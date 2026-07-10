# Validation des resultats - Cas d'etude 1

| Date | 2026-07-02 |
| --- | --- |
| Base | POC_ETL_IA |
| Statut global | VALIDE |

## 1. Couche SQL (chargement manuel)

### Chargement staging

| Controle | Attendu | Observe | Statut |
| --- | --- | --- | --- |
| Lignes en staging | 4 | 4 | OK |
| batch_id | 1 | 1 | OK |
| source_system | ERP_CUSTOMER | ERP_CUSTOMER | OK |
| Statut run log | SUCCESS | SUCCESS | OK |
| row_count | 4 | 4 | OK |

### Controles qualite (apres chargement SQL manuel)

| Controle | Attendu | Observe | Statut |
| --- | --- | --- | --- |
| total_rows | 4 | 4 | OK |
| null_customer_id | 0 | 0 | OK |
| doublon C001 | 2 | 2 | OK |
| invalid_country | 0 | 0 | OK |

## 2. Couche SSIS (package PKG_SRC_CUSTOMER_STG_SALES_CUSTOMER)

### Execution du package

| Controle | Attendu | Observe | Statut |
| --- | --- | --- | --- |
| run_id | - | 2 | OK |
| Statut run log | SUCCESS | SUCCESS | OK |
| row_count_in | 4 | 4 | OK |
| row_count_out | 4 | 4 | OK |
| created_by | nesrine | nesrine | OK |
| Date execution | - | 2026-07-02 13:44:59 | OK |

### Controles qualite (apres chargement SSIS)

| Controle | Attendu | Observe | Statut |
| --- | --- | --- | --- |
| total_rows | 4 | 4 | OK |
| null_customer_id | 0 | 0 | OK |
| doublon C001 | 2 | 2 | OK |
| invalid_country | 0 | 0 | OK |

### Interpretation

Les resultats SSIS sont **identiques** a la couche SQL manuelle : le package reproduit correctement le flux source-to-staging. Les anomalies metier attendues (doublon C001) sont toujours detectees — ce qui confirme que les controles qualite fonctionnent apres l'ETL automatise.

## Objets utilises

- dbo.src_customer
- dbo.stg_sales_customer
- dbo.etl_run_log
- dbo.etl_error_log
- Package SSIS : PKG_SRC_CUSTOMER_STG_SALES_CUSTOMER

## Conclusion

Le Cas d'etude 1 est valide sur les deux approches (SQL manuel + SSIS). Prochaine etape : comparaison manuel vs IA, puis Power BI.
