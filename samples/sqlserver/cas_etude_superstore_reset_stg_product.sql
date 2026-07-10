/*
Reset staging produit avant execution PKG_DIM_PRODUCT (7B-4)
Ne touche pas raw_superstore ni stg_dim_customer.
*/
USE POC_ETL_IA;
GO

TRUNCATE TABLE stg_dim_product;

DELETE FROM etl_reject_log
WHERE package_name = 'PKG_DIM_PRODUCT';

DELETE FROM etl_run_log
WHERE package_name = 'PKG_DIM_PRODUCT';
GO

SELECT COUNT(*) AS raw_rows FROM raw_superstore;
SELECT COUNT(*) AS stg_dim_product_rows FROM stg_dim_product;
GO
