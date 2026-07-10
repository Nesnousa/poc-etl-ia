/*
Reset staging client avant execution PKG_DIM_CUSTOMER (7B-3)
Ne touche pas raw_superstore.
*/
USE POC_ETL_IA;
GO

TRUNCATE TABLE stg_dim_customer;

DELETE FROM etl_reject_log
WHERE package_name = 'PKG_DIM_CUSTOMER';

DELETE FROM etl_run_log
WHERE package_name = 'PKG_DIM_CUSTOMER';
GO

SELECT COUNT(*) AS raw_rows FROM raw_superstore;
SELECT COUNT(*) AS stg_dim_customer_rows FROM stg_dim_customer;
GO
