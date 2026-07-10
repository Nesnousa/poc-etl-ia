/*
Reset staging fait avant execution PKG_FACT_SALES (7B-4)
Ne touche pas raw_superstore ni les dimensions.
*/
USE POC_ETL_IA;
GO

TRUNCATE TABLE stg_fact_sales;

DELETE FROM etl_reject_log
WHERE package_name = 'PKG_FACT_SALES';

DELETE FROM etl_run_log
WHERE package_name = 'PKG_FACT_SALES';
GO

SELECT COUNT(*) AS raw_rows FROM raw_superstore;
SELECT COUNT(*) AS stg_fact_sales_rows FROM stg_fact_sales;
GO
