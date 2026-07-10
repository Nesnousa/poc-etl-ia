/*
Cas d'etude Superstore - Phase 7B-1
Setup des tables landing, staging et rejets.

Executer dans la base POC_ETL_IA.
Ordre :
  1) ce script
  2) ingest Python (7B-2) -> raw_superstore
  3) packages SSIS (7B-3 / 7B-4)

Note : ne supprime pas les objets du Cas d'etude 1 (src_customer, stg_sales_customer).
*/

USE POC_ETL_IA;
GO

-- =============================================================================
-- 1. Landing - copie structuree du CSV Superstore
-- =============================================================================
IF OBJECT_ID('raw_superstore', 'U') IS NOT NULL
    DROP TABLE raw_superstore;
GO

CREATE TABLE raw_superstore (
    row_id              INT             NOT NULL,
    order_id            NVARCHAR(50)    NOT NULL,
    order_date          DATE            NULL,
    ship_date           DATE            NULL,
    ship_mode           NVARCHAR(50)    NULL,
    customer_id         NVARCHAR(50)    NULL,
    customer_name       NVARCHAR(255)   NULL,
    segment             NVARCHAR(50)    NULL,
    country             NVARCHAR(100)   NULL,
    city                NVARCHAR(100)   NULL,
    state               NVARCHAR(100)   NULL,
    postal_code         NVARCHAR(20)    NULL,
    region              NVARCHAR(50)    NULL,
    product_id          NVARCHAR(50)    NULL,
    category            NVARCHAR(100)   NULL,
    sub_category        NVARCHAR(100)   NULL,
    product_name        NVARCHAR(255)   NULL,
    sales               DECIMAL(18, 2)  NULL,
    quantity            INT             NULL,
    discount            DECIMAL(18, 4)  NULL,
    profit              DECIMAL(18, 2)  NULL,
    source_file         NVARCHAR(255)   NULL,
    ingest_batch_id     INT             NOT NULL DEFAULT 1,
    ingest_ts           DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_raw_superstore PRIMARY KEY (row_id)
);
GO

CREATE INDEX IX_raw_superstore_customer_id ON raw_superstore (customer_id);
CREATE INDEX IX_raw_superstore_product_id ON raw_superstore (product_id);
CREATE INDEX IX_raw_superstore_order_id ON raw_superstore (order_id);
GO

-- =============================================================================
-- 2. Staging dimensions et fait
-- =============================================================================
IF OBJECT_ID('stg_dim_customer', 'U') IS NOT NULL
    DROP TABLE stg_dim_customer;
GO

CREATE TABLE stg_dim_customer (
    batch_id              INT             NOT NULL,
    source_system         NVARCHAR(100)   NOT NULL,
    customer_id           NVARCHAR(50)    NOT NULL,
    customer_name         NVARCHAR(255)   NULL,
    customer_name_clean   NVARCHAR(255)   NULL,
    segment               NVARCHAR(50)    NULL,
    country               NVARCHAR(100)   NULL,
    city                  NVARCHAR(100)   NULL,
    state                 NVARCHAR(100)   NULL,
    postal_code           NVARCHAR(20)    NULL,
    region                NVARCHAR(50)    NULL,
    is_active             BIT             NOT NULL DEFAULT 1,
    load_ts               DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

CREATE INDEX IX_stg_dim_customer_batch ON stg_dim_customer (batch_id);
CREATE INDEX IX_stg_dim_customer_id ON stg_dim_customer (customer_id);
GO

IF OBJECT_ID('stg_dim_product', 'U') IS NOT NULL
    DROP TABLE stg_dim_product;
GO

CREATE TABLE stg_dim_product (
    batch_id          INT             NOT NULL,
    source_system     NVARCHAR(100)   NOT NULL,
    product_id        NVARCHAR(50)    NOT NULL,
    product_name      NVARCHAR(255)   NULL,
    category          NVARCHAR(100)   NULL,
    sub_category      NVARCHAR(100)   NULL,
    load_ts           DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

CREATE INDEX IX_stg_dim_product_batch ON stg_dim_product (batch_id);
CREATE INDEX IX_stg_dim_product_id ON stg_dim_product (product_id);
GO

IF OBJECT_ID('stg_fact_sales', 'U') IS NOT NULL
    DROP TABLE stg_fact_sales;
GO

CREATE TABLE stg_fact_sales (
    batch_id          INT             NOT NULL,
    source_system     NVARCHAR(100)   NOT NULL,
    row_id            INT             NOT NULL,
    order_id          NVARCHAR(50)    NOT NULL,
    order_date        DATE            NULL,
    ship_date         DATE            NULL,
    ship_mode         NVARCHAR(50)    NULL,
    customer_id       NVARCHAR(50)    NOT NULL,
    product_id        NVARCHAR(50)    NOT NULL,
    sales             DECIMAL(18, 2)  NULL,
    quantity          INT             NULL,
    discount          DECIMAL(18, 4)  NULL,
    profit            DECIMAL(18, 2)  NULL,
    margin_pct        DECIMAL(18, 4)  NULL,
    load_ts           DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_stg_fact_sales PRIMARY KEY (batch_id, row_id)
);
GO

CREATE INDEX IX_stg_fact_sales_customer ON stg_fact_sales (customer_id);
CREATE INDEX IX_stg_fact_sales_product ON stg_fact_sales (product_id);
CREATE INDEX IX_stg_fact_sales_order ON stg_fact_sales (order_id);
GO

-- =============================================================================
-- 3. Journal des rejets (lignes invalides SSIS)
-- =============================================================================
IF OBJECT_ID('etl_reject_log', 'U') IS NULL
BEGIN
    CREATE TABLE etl_reject_log (
        reject_id         INT IDENTITY(1,1) PRIMARY KEY,
        run_id            INT             NULL,
        package_name      NVARCHAR(255)   NOT NULL,
        step_name         NVARCHAR(255)   NOT NULL,
        reject_reason     NVARCHAR(500)   NOT NULL,
        business_key      NVARCHAR(100)   NULL,
        row_id            INT             NULL,
        payload_json      NVARCHAR(MAX)   NULL,
        reject_ts         DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME()
    );
END;
GO

-- =============================================================================
-- 4. Framework logging (preserve si deja present)
-- =============================================================================
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

CREATE OR ALTER PROCEDURE usp_log_etl_reject
    @run_id INT = NULL,
    @package_name NVARCHAR(255),
    @step_name NVARCHAR(255),
    @reject_reason NVARCHAR(500),
    @business_key NVARCHAR(100) = NULL,
    @row_id INT = NULL,
    @payload_json NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO etl_reject_log (
        run_id, package_name, step_name, reject_reason,
        business_key, row_id, payload_json
    )
    VALUES (
        @run_id, @package_name, @step_name, @reject_reason,
        @business_key, @row_id, @payload_json
    );
END;
GO

-- =============================================================================
-- 5. Vues d'extraction pour SSIS
-- =============================================================================
CREATE OR ALTER VIEW vw_extract_superstore_customers
AS
SELECT DISTINCT
    customer_id,
    customer_name,
    segment,
    country,
    city,
    state,
    postal_code,
    region
FROM raw_superstore
WHERE customer_id IS NOT NULL;
GO

CREATE OR ALTER VIEW vw_extract_superstore_products
AS
SELECT DISTINCT
    product_id,
    product_name,
    category,
    sub_category
FROM raw_superstore
WHERE product_id IS NOT NULL;
GO

CREATE OR ALTER VIEW vw_extract_superstore_sales
AS
SELECT
    row_id,
    order_id,
    order_date,
    ship_date,
    ship_mode,
    customer_id,
    product_id,
    sales,
    quantity,
    discount,
    profit
FROM raw_superstore;
GO

-- =============================================================================
-- 6. Verification post-setup
-- =============================================================================
SELECT 'raw_superstore' AS object_name, COUNT(*) AS row_count FROM raw_superstore
UNION ALL
SELECT 'stg_dim_customer', COUNT(*) FROM stg_dim_customer
UNION ALL
SELECT 'stg_dim_product', COUNT(*) FROM stg_dim_product
UNION ALL
SELECT 'stg_fact_sales', COUNT(*) FROM stg_fact_sales;
GO

PRINT 'Cas etude Superstore 7B-1 : setup termine. Tables vides en attente de l''ingest Python (7B-2).';
GO
