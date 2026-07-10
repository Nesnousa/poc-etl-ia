/*
Cas d'etude 1 - Chargement source vers staging avec logging
*/

DECLARE @batch_id INT = 1;
DECLARE @source_system NVARCHAR(100) = 'ERP_CUSTOMER';
DECLARE @package_name NVARCHAR(255) = 'PKG_SRC_CUSTOMER_STG_SALES_CUSTOMER';
DECLARE @created_by NVARCHAR(100) = 'nesrine';
DECLARE @run_id INT;
DECLARE @row_count_in INT;
DECLARE @row_count_out INT;

-- Demarrage du run
CREATE TABLE #run_start (run_id INT);
INSERT INTO #run_start
EXEC usp_log_etl_run_start
    @package_name = @package_name,
    @source_system = @source_system,
    @created_by = @created_by;

SELECT @run_id = run_id FROM #run_start;
DROP TABLE #run_start;

SELECT @row_count_in = COUNT(*) FROM src_customer;

BEGIN TRY
    INSERT INTO stg_sales_customer (
        batch_id,
        source_system,
        customer_id,
        customer_code,
        customer_name,
        country_code,
        email_address,
        source_extract_ts,
        load_ts
    )
    SELECT
        @batch_id,
        @source_system,
        customer_id,
        customer_code,
        customer_name,
        country_code,
        email_address,
        updated_at,
        SYSUTCDATETIME()
    FROM src_customer;

    SELECT @row_count_out = COUNT(*)
    FROM stg_sales_customer
    WHERE batch_id = @batch_id;

    EXEC usp_log_etl_run_end
        @run_id = @run_id,
        @status = 'SUCCESS',
        @row_count_in = @row_count_in,
        @row_count_out = @row_count_out;
END TRY
BEGIN CATCH
    INSERT INTO etl_error_log (run_id, step_name, error_message)
    VALUES (@run_id, 'LOAD_STAGING', ERROR_MESSAGE());

    EXEC usp_log_etl_run_end
        @run_id = @run_id,
        @status = 'FAILED',
        @row_count_in = @row_count_in,
        @row_count_out = NULL;

    THROW;
END CATCH;

-- Verification rapide
SELECT * FROM stg_sales_customer WHERE batch_id = @batch_id;
SELECT * FROM etl_run_log WHERE run_id = @run_id;
