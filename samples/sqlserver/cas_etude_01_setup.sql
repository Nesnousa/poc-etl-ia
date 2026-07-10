/*
Cas d'etude 1 - Setup complet
Executer dans la base POC_ETL_IA
Ordre : 1) ce script, 2) cas_etude_01_load_staging.sql
*/

-- 1. Table source
IF OBJECT_ID('src_customer', 'U') IS NOT NULL
    DROP TABLE src_customer;
GO

CREATE TABLE src_customer (
    customer_id     INT             NOT NULL,
    customer_code   NVARCHAR(50)    NOT NULL,
    customer_name   NVARCHAR(255)   NOT NULL,
    country_code    NVARCHAR(10)    NULL,
    email_address   NVARCHAR(255)   NULL,
    updated_at      DATETIME2       NOT NULL
);
GO

INSERT INTO src_customer (customer_id, customer_code, customer_name, country_code, email_address, updated_at)
VALUES
    (1, 'C001', 'Alpha Retail', 'FR', 'contact@alpha.fr', '2026-06-01T08:00:00'),
    (2, 'C002', 'Beta Services', 'DE', 'info@beta.de', '2026-06-01T08:00:00'),
    (3, 'C003', 'Gamma Corp', 'US', NULL, '2026-06-01T08:00:00'),
    (4, 'C001', 'Alpha Retail Duplicate', 'FR', 'dup@alpha.fr', '2026-06-01T08:00:00');
GO

-- 2. Table staging
IF OBJECT_ID('stg_sales_customer', 'U') IS NOT NULL
    DROP TABLE stg_sales_customer;
GO

CREATE TABLE stg_sales_customer (
    batch_id            INT             NOT NULL,
    source_system       NVARCHAR(100)   NOT NULL,
    customer_id         INT             NULL,
    customer_code       NVARCHAR(50)    NULL,
    customer_name       NVARCHAR(255)   NULL,
    country_code        NVARCHAR(10)    NULL,
    email_address       NVARCHAR(255)   NULL,
    source_extract_ts   DATETIME2       NOT NULL,
    load_ts             DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

CREATE INDEX IX_stg_sales_customer_batch_id
    ON stg_sales_customer (batch_id);
GO

-- 3. Framework de logging
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

    INSERT INTO etl_run_log (package_name, source_system, status, created_by)
    VALUES (@package_name, @source_system, 'STARTED', @created_by);

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
