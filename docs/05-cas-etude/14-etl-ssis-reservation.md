# ETL Réservations — Source → Staging → Data Warehouse (SSIS + SQL + IA/MCP)

| Élément | Valeur |
| --- | --- |
| Objectif | Alimenter le staging depuis la source, puis le DW depuis le staging, selon la modélisation en étoile |
| Domaine d'exemple | Réservations d'hôtel (générique, adaptable à tout projet) |
| Deux chemins | (A) ETL en **procédures SQL** exécutables par Claude via MCP ; (B) **package SSIS** source→staging à ouvrir dans Visual Studio |
| Livrables SQL | `samples/sqlserver/reservation_etl_setup.sql`, `samples/sqlserver/reservation_etl_procedures.sql` |
| Livrables SSIS | `ssis/reservation/generate_ssis_stg_reservation.py`, `ssis/POC_ETL_IA_SSIS/PKG_STG_RESERVATION.dtsx` |
| Statut | ETL SQL **testé** sur `POC_ETL_IA` ; package SSIS **généré** (à exécuter dans Visual Studio) |

## 1. Architecture du pipeline

```
[SOURCE / LANDING]  raw_hotel_reservation      (copie brute, type CSV, non typée)
        |
        |  Étape 1 : source -> staging
        |     - Chemin A : usp_load_stg_hotel_reservation  (SQL, via Claude/MCP)
        |     - Chemin B : package SSIS PKG_STG_RESERVATION (Visual Studio)
        v
[STAGING]           stg_hotel_reservation      (typé + traçabilité batch_id/source_system/load_ts)
        |
        |  Étape 2 : staging -> DW (procédures SQL)
        |     usp_load_dim_client / usp_load_dim_chambre / usp_load_dim_date
        |     usp_load_fact_reservation  (résolution des clés de substitution)
        v
[DW en étoile]      dim_client / dim_chambre / dim_date  +  fact_reservation (FK vers les 3 dimensions)
```

Orchestration complète en une commande : `EXEC usp_run_reservation_etl;`

## 2. La question du « connecteur » pour Claude Max (à connaître)

Souhait exprimé : tout faire avec Claude **sans rien toucher depuis le PC**, puis voir les résultats. Voici la réalité technique, vérifiée :

| Besoin | Existe-t-il un connecteur ? | Réponse |
| --- | --- | --- |
| Claude **exécute du SQL** sur SQL Server (créer tables, lancer l'ETL) | **Oui** — serveur **MCP SQL Server** (ex. `mssql-mcp` via `npx`) | ✅ Chemin A entièrement « no-touch » |
| Claude **génère un package SSIS** (`.dtsx`) tout seul | **Non** | ❌ Pas de MCP qui crée des packages SSIS |
| Claude **lit / migre** des packages SSIS existants | Oui (ex. `ssis-adf-agent` : SSIS → Azure Data Factory ; skills SSIS → Databricks) | ⚠️ Analyse/migration seulement |

**Conséquence** : le package SSIS (`.dtsx`) est produit par **Cursor** (script Python générateur, comme les packages Superstore) puis ouvert dans **Visual Studio**. En revanche, tout l'ETL en **procédures SQL** peut être créé ET exécuté par **Claude via MCP**, ce qui répond au « sans rien toucher » et « voir les résultats dans SSMS ».

## 3. Chemin A — ETL par procédures SQL (démo « no-touch » via Claude/MCP)

1. Serveur MCP SQL Server actif dans Claude (voir `docs/05-cas-etude/13-demo-ia-mcp-sql-staging-dw.md`, §4).
2. Demander à Claude d'exécuter, dans l'ordre :
   - `reservation_etl_setup.sql` (crée raw + staging + DW + vue, alimente la source) ;
   - `reservation_etl_procedures.sql` (crée les procédures ETL) ;
   - `EXEC usp_run_reservation_etl;` (lance tout l'ETL).
3. Vérifier dans SSMS : les tables `stg_*`, `dim_*`, `fact_reservation` se remplissent.

### Résultat testé (sur POC_ETL_IA)

| Table | Type | Lignes |
| --- | --- | --- |
| `raw_hotel_reservation` | Source (brut) | 6 (dont 1 doublon) |
| `stg_hotel_reservation` | Staging | 6 |
| `dim_client` | Dimension | 4 (dédoublonnée) |
| `dim_chambre` | Dimension | 3 |
| `dim_date` | Dimension (date) | 5 |
| `fact_reservation` | Faits | 5 (relié aux 3 dimensions) |

Nettoyage automatique constaté : noms « `  jean dupont ` » → « `Jean dupont` », doublon `RES-001` éliminé, `montant_par_nuit` calculé.

## 4. Chemin B — Package SSIS source → staging

Le package `PKG_STG_RESERVATION` reproduit exactement le pattern des packages Superstore :

```
Control Flow : SQL_StartRun -> SQL_CountSource -> SQL_LogRejects -> DFT_LoadReservation -> SQL_EndRunSuccess
Data Flow    : OLE DB Source (vw_extract_hotel_reservation) -> RC_Valid (Row Count) -> OLE DB Destination (stg_hotel_reservation)
Event OnError: SQL_LogError -> etl_error_log
```

### Comment l'exécuter dans Visual Studio

1. (Re)générer si besoin : `python ssis/reservation/generate_ssis_stg_reservation.py`.
2. Créer les tables : exécuter `reservation_etl_setup.sql` dans SSMS.
3. Ouvrir `ssis/POC_ETL_IA_SSIS.sln`, vérifier la connexion `CM_POC_ETL_IA` (serveur, base).
4. Clic droit sur `PKG_STG_RESERVATION.dtsx` → **Execute Package**.
5. Contrôler : `stg_hotel_reservation` alimentée, run tracé dans `etl_run_log`.
6. (Optionnel) enchaîner staging → DW avec les procédures du Chemin A.

> Le package est déjà déclaré dans le projet (`POC_ETL_IA_SSIS.dtproj`). Le runtime SSIS complet peut être nécessaire (édition non-Express) pour `dtexec` en ligne de commande ; sinon, exécuter dans Visual Studio.

## 5. Version générique (tout type de projet)

Pour un **autre domaine**, remplacer les entités :

| Élément réservation | À remplacer par… |
| --- | --- |
| `raw_hotel_reservation` / `stg_hotel_reservation` | votre source / votre staging |
| `dim_client`, `dim_chambre`, `dim_date` | vos axes d'analyse (dimensions) |
| `fact_reservation` | votre événement mesuré (table de faits) |
| `nb_nuits`, `montant` | vos mesures |

Templates génériques associés :
- `templates/ssis/source_to_staging_template.md` — structure d'un package source→staging.
- `templates/sql/staging_table_template.sql` — table de staging générique.
- `templates/logging/etl_logging_framework.sql` — cadre de journalisation.
- `prompts/prompt_claude_mcp_staging_dw.md` — prompt IA générique (staging + DW via MCP).

## 6. Ce que cette étape prouve

1. **Le pipeline complet** (source → staging → DW) est réalisable des deux façons : SSIS (outil visuel) et SQL (automatisable par IA).
2. **L'IA peut exécuter tout l'ETL SQL** via MCP, sans intervention manuelle, résultats visibles dans SSMS.
3. **SSIS n'est pas automatisable par MCP pour la création** : le `.dtsx` est généré par script, ce qui reste reproductible et versionnable.
4. **Générique** : la même démarche s'applique à n'importe quel projet en changeant les entités.

## 7. Limites et vigilance

- Accès **en écriture** d'une IA à une base : à réserver à un environnement de test, compte à privilèges limités.
- Toujours **relire** le SQL généré par l'IA avant exécution.
- Le nettoyage illustré (casse/espaces) est volontairement simple ; un cas réel demande des règles qualité plus complètes (cf. `templates/quality/data_quality_checks_template.sql`).
