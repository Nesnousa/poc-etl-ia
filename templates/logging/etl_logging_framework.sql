/* =====================================================================
   TEMPLATE GÉNÉRIQUE — Cadre de journalisation (logging) ETL
   ---------------------------------------------------------------------
   Objectif : tracer chaque exécution ETL (début, fin, statut, volumes)
   et centraliser les erreurs. Réutilisable TEL QUEL sur tout projet :
   les noms de tables (etl_run_log, etl_error_log) et de procédures sont
   des standards à conserver d'un projet à l'autre.

   Usage :
   1. Exécuter ce script une fois par base pour créer les tables + procédures.
   2. Dans chaque package/flux : appeler usp_log_etl_run_start au début
      (récupère un run_id) puis usp_log_etl_run_end à la fin.
   ===================================================================== */

IF OBJECT_ID('etl_run_log', 'U') IS NULL
BEGIN
    CREATE TABLE etl_run_log (
        run_id               INT IDENTITY(1,1) PRIMARY KEY,
        package_name         NVARCHAR(255) NOT NULL,
        source_system        NVARCHAR(100) NULL,
        start_ts             DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        end_ts               DATETIME2 NULL,
        status               NVARCHAR(30) NOT NULL,
        row_count_in         INT NULL,
        row_count_out        INT NULL,
        created_by           NVARCHAR(100) NULL
    );
END;
GO

IF OBJECT_ID('etl_error_log', 'U') IS NULL
BEGIN
    CREATE TABLE etl_error_log (
        error_id             INT IDENTITY(1,1) PRIMARY KEY,
        run_id               INT NOT NULL,
        step_name            NVARCHAR(255) NOT NULL,
        error_message        NVARCHAR(MAX) NOT NULL,
        error_ts             DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
END;
GO

CREATE OR ALTER PROCEDURE usp_log_etl_run_start
    @package_name NVARCHAR(255),
    @source_system NVARCHAR(100),
    @created_by NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO etl_run_log (
        package_name,
        source_system,
        status,
        created_by
    )
    VALUES (
        @package_name,
        @source_system,
        'STARTED',
        @created_by
    );

    SELECT SCOPE_IDENTITY() AS run_id;
END;
GO

CREATE OR ALTER PROCEDURE usp_log_etl_run_end
    @run_id INT,
    @status NVARCHAR(30),
    @row_count_in INT = NULL,
    @row_count_out INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE etl_run_log
    SET end_ts = SYSUTCDATETIME(),
        status = @status,
        row_count_in = @row_count_in,
        row_count_out = @row_count_out
    WHERE run_id = @run_id;
END;
GO
