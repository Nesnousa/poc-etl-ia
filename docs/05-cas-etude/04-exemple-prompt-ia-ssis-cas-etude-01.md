# Exemple de prompt IA rempli - Cas d'etude 1

Utiliser ce prompt dans Cursor pour tester l'assistance IA sur le package SSIS.

---

Tu es un expert SSIS, SQL Server et Data Engineering.

Ta mission est de proposer un template SSIS reutilisable pour un flux ETL.

## Contexte

- Source : `OLE DB - table src_customer dans POC_ETL_IA`
- Cible : `stg_sales_customer`
- Pattern ETL : `source-to-staging`
- Colonnes principales :
  - customer_id (INT)
  - customer_code (NVARCHAR 50)
  - customer_name (NVARCHAR 255)
  - country_code (NVARCHAR 10)
  - email_address (NVARCHAR 255)
  - updated_at (DATETIME2)
- Colonnes ajoutees en staging :
  - batch_id (INT)
  - source_system (NVARCHAR 100)
  - source_extract_ts (DATETIME2)
  - load_ts (DATETIME2)
- Regles de qualite :
  - detecter les doublons sur customer_code
  - verifier les nulls sur customer_id
  - verifier le format country_code (2 caracteres)
- Besoins de logging :
  - demarrer un run via usp_log_etl_run_start
  - cloturer via usp_log_etl_run_end
  - journaliser les erreurs dans etl_error_log

## Contraintes

- Ne pas inventer de metadonnees absentes.
- Utiliser des composants SSIS standards.
- Inclure Control Flow et Data Flow detailles.
- Inclure les variables du package.
- Inclure la gestion d'erreur OnError.

## Sortie attendue

1. Description du package
2. Structure Control Flow
3. Structure Data Flow avec mapping des colonnes
4. Liste des variables
5. Gestion d'erreur
6. Points de revue humaine

---

## Apres generation IA

Comparer la sortie avec `docs/02-ssis/02-guide-creation-package-ssis.md` et noter :

- elements corrects du premier coup
- elements a corriger manuellement
- temps gagne ou non
