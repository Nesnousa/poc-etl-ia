/* =====================================================================
   ETL RÉSERVATIONS — PROCÉDURES (exécutables par Claude via MCP)
   ---------------------------------------------------------------------
   Ces procédures réalisent tout l'ETL en T-SQL, donc SANS SSIS :
   c'est le chemin « no-touch » où un assistant IA (Claude), connecté à
   SQL Server via un serveur MCP, peut TOUT exécuter à distance, et l'on
   voit les résultats dans SSMS.

     usp_load_stg_hotel_reservation  : raw   -> staging  (typage + traçabilité)
     usp_load_dim_client             : staging -> dim_client  (dédoublonnage + nettoyage)
     usp_load_dim_chambre            : staging -> dim_chambre
     usp_load_dim_date               : staging -> dim_date
     usp_load_fact_reservation       : staging -> fait (résolution des clés de substitution)
     usp_run_reservation_etl         : orchestre tout dans l'ordre

   Pré-requis : reservation_etl_setup.sql exécuté, et le cadre de
   journalisation (etl_run_log / usp_log_etl_run_start / _end) présent.
   ===================================================================== */

USE POC_ETL_IA;
GO

-- ---------------------------------------------------------------------
-- 1. raw -> staging
-- ---------------------------------------------------------------------
CREATE OR ALTER PROCEDURE usp_load_stg_hotel_reservation
    @batch_id INT = 1
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @run_id INT;
    EXEC usp_log_etl_run_start @package_name = N'PROC_STG_RESERVATION',
                               @source_system = N'DEMO_HOTEL', @created_by = N'claude_mcp';
    SELECT @run_id = MAX(run_id) FROM etl_run_log WHERE package_name = N'PROC_STG_RESERVATION';

    DELETE FROM stg_hotel_reservation WHERE batch_id = @batch_id;

    INSERT INTO stg_hotel_reservation
        (batch_id, source_system, reservation_id, client_id, client_nom, client_ville,
         client_pays, chambre_id, type_chambre, capacite, date_arrivee, nb_nuits, montant)
    SELECT
        @batch_id, N'DEMO_HOTEL', reservation_id, client_id, client_nom, client_ville,
        client_pays, chambre_id, type_chambre,
        TRY_CAST(capacite AS INT),
        TRY_CAST(date_arrivee AS DATE),
        TRY_CAST(nb_nuits AS INT),
        TRY_CAST(montant AS DECIMAL(18, 4))
    FROM raw_hotel_reservation
    WHERE reservation_id IS NOT NULL;

    DECLARE @n INT = (SELECT COUNT(*) FROM stg_hotel_reservation WHERE batch_id = @batch_id);
    EXEC usp_log_etl_run_end @run_id = @run_id, @status = 'SUCCESS',
                             @row_count_in = @n, @row_count_out = @n;
END;
GO

-- ---------------------------------------------------------------------
-- 2. staging -> dim_client (dédoublonnage + nettoyage du nom)
-- ---------------------------------------------------------------------
CREATE OR ALTER PROCEDURE usp_load_dim_client
    @batch_id INT = 1
AS
BEGIN
    SET NOCOUNT ON;
    WITH dedup AS (
        SELECT client_id, client_nom, LTRIM(RTRIM(client_nom)) AS nom_trim,
               client_ville, client_pays, source_system,
               ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY load_ts DESC) AS rn
        FROM stg_hotel_reservation
        WHERE batch_id = @batch_id
    )
    MERGE dim_client AS cible
    USING (
        SELECT client_id, client_nom,
               UPPER(LEFT(nom_trim, 1)) + LOWER(SUBSTRING(nom_trim, 2, 255)) AS nom_clean,
               client_ville, client_pays, source_system
        FROM dedup WHERE rn = 1
    ) AS src
    ON cible.client_id = src.client_id
    WHEN MATCHED THEN UPDATE SET
        cible.client_nom = src.client_nom,
        cible.client_nom_clean = src.nom_clean,
        cible.ville = src.client_ville,
        cible.pays = src.client_pays,
        cible.source_system = src.source_system,
        cible.dw_load_ts = SYSUTCDATETIME()
    WHEN NOT MATCHED BY TARGET THEN
        INSERT (client_id, client_nom, client_nom_clean, ville, pays, valid_from, is_current, source_system, dw_load_ts)
        VALUES (src.client_id, src.client_nom, src.nom_clean, src.client_ville, src.client_pays,
                SYSUTCDATETIME(), 1, src.source_system, SYSUTCDATETIME());
END;
GO

-- ---------------------------------------------------------------------
-- 3. staging -> dim_chambre
-- ---------------------------------------------------------------------
CREATE OR ALTER PROCEDURE usp_load_dim_chambre
    @batch_id INT = 1
AS
BEGIN
    SET NOCOUNT ON;
    WITH dedup AS (
        SELECT chambre_id, type_chambre, capacite, source_system,
               ROW_NUMBER() OVER (PARTITION BY chambre_id ORDER BY load_ts DESC) AS rn
        FROM stg_hotel_reservation
        WHERE batch_id = @batch_id
    )
    MERGE dim_chambre AS cible
    USING (SELECT chambre_id, type_chambre, capacite, source_system FROM dedup WHERE rn = 1) AS src
    ON cible.chambre_id = src.chambre_id
    WHEN MATCHED THEN UPDATE SET
        cible.type_chambre = src.type_chambre,
        cible.capacite = src.capacite,
        cible.source_system = src.source_system,
        cible.dw_load_ts = SYSUTCDATETIME()
    WHEN NOT MATCHED BY TARGET THEN
        INSERT (chambre_id, type_chambre, capacite, source_system, dw_load_ts)
        VALUES (src.chambre_id, src.type_chambre, src.capacite, src.source_system, SYSUTCDATETIME());
END;
GO

-- ---------------------------------------------------------------------
-- 4. staging -> dim_date
-- ---------------------------------------------------------------------
CREATE OR ALTER PROCEDURE usp_load_dim_date
    @batch_id INT = 1
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dim_date (date_key, date_complete, annee, mois, jour)
    SELECT DISTINCT
        YEAR(date_arrivee) * 10000 + MONTH(date_arrivee) * 100 + DAY(date_arrivee),
        date_arrivee, YEAR(date_arrivee), MONTH(date_arrivee), DAY(date_arrivee)
    FROM stg_hotel_reservation s
    WHERE s.batch_id = @batch_id AND s.date_arrivee IS NOT NULL
      AND NOT EXISTS (SELECT 1 FROM dim_date d WHERE d.date_complete = s.date_arrivee);
END;
GO

-- ---------------------------------------------------------------------
-- 5. staging -> fait (résolution des clés de substitution par lookup)
-- ---------------------------------------------------------------------
CREATE OR ALTER PROCEDURE usp_load_fact_reservation
    @batch_id INT = 1
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @run_id INT;
    EXEC usp_log_etl_run_start @package_name = N'PROC_FACT_RESERVATION',
                               @source_system = N'DEMO_HOTEL', @created_by = N'claude_mcp';
    SELECT @run_id = MAX(run_id) FROM etl_run_log WHERE package_name = N'PROC_FACT_RESERVATION';

    WITH dedup AS (
        SELECT reservation_id, client_id, chambre_id, date_arrivee, nb_nuits, montant,
               ROW_NUMBER() OVER (PARTITION BY reservation_id ORDER BY load_ts DESC) AS rn
        FROM stg_hotel_reservation
        WHERE batch_id = @batch_id
    )
    INSERT INTO fact_reservation
        (reservation_id, client_key, chambre_key, date_key, nb_nuits, montant, montant_par_nuit)
    SELECT
        r.reservation_id, c.client_key, ch.chambre_key, d.date_key,
        r.nb_nuits,
        CAST(r.montant AS DECIMAL(18, 2)),
        CAST(r.montant / NULLIF(r.nb_nuits, 0) AS DECIMAL(18, 2))
    FROM dedup r
    JOIN dim_client  c  ON r.client_id  = c.client_id
    JOIN dim_chambre ch ON r.chambre_id = ch.chambre_id
    JOIN dim_date    d  ON r.date_arrivee = d.date_complete
    WHERE r.rn = 1;

    DECLARE @n INT = (SELECT COUNT(*) FROM fact_reservation);
    EXEC usp_log_etl_run_end @run_id = @run_id, @status = 'SUCCESS',
                             @row_count_in = @n, @row_count_out = @n;
END;
GO

-- ---------------------------------------------------------------------
-- 6. Orchestration complète (rejouable)
-- ---------------------------------------------------------------------
CREATE OR ALTER PROCEDURE usp_run_reservation_etl
    @batch_id INT = 1
AS
BEGIN
    SET NOCOUNT ON;

    -- Réinitialisation (ordre des clés étrangères) pour un run propre
    DELETE FROM fact_reservation;
    DELETE FROM dim_client;
    DELETE FROM dim_chambre;
    DELETE FROM dim_date;
    DBCC CHECKIDENT ('fact_reservation', RESEED, 0) WITH NO_INFOMSGS;
    DBCC CHECKIDENT ('dim_client', RESEED, 0) WITH NO_INFOMSGS;
    DBCC CHECKIDENT ('dim_chambre', RESEED, 0) WITH NO_INFOMSGS;

    EXEC usp_load_stg_hotel_reservation @batch_id = @batch_id;   -- raw -> staging
    EXEC usp_load_dim_client            @batch_id = @batch_id;   -- staging -> dimensions
    EXEC usp_load_dim_chambre           @batch_id = @batch_id;
    EXEC usp_load_dim_date              @batch_id = @batch_id;
    EXEC usp_load_fact_reservation      @batch_id = @batch_id;   -- staging -> fait

    -- Synthèse
    SELECT 'raw_hotel_reservation' AS objet, COUNT(*) AS lignes FROM raw_hotel_reservation
    UNION ALL SELECT 'stg_hotel_reservation', COUNT(*) FROM stg_hotel_reservation
    UNION ALL SELECT 'dim_client',       COUNT(*) FROM dim_client
    UNION ALL SELECT 'dim_chambre',      COUNT(*) FROM dim_chambre
    UNION ALL SELECT 'dim_date',         COUNT(*) FROM dim_date
    UNION ALL SELECT 'fact_reservation', COUNT(*) FROM fact_reservation;
END;
GO

PRINT 'Procédures ETL réservations créées. Lancer : EXEC usp_run_reservation_etl;';
GO
