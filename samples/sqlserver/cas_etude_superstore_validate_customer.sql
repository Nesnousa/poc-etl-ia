/*
Validation post PKG_DIM_CUSTOMER (7B-3)
*/
USE POC_ETL_IA;
GO

SELECT COUNT(*) AS raw_rows FROM raw_superstore;
SELECT COUNT(DISTINCT customer_id) AS distinct_customers_raw FROM raw_superstore WHERE customer_id IS NOT NULL;
SELECT COUNT(*) AS extract_view_rows FROM vw_extract_superstore_customers;
SELECT COUNT(*) AS stg_dim_customer_rows FROM stg_dim_customer;

SELECT TOP 5
    customer_id,
    customer_name,
    customer_name_clean,
    segment,
    region,
    load_ts
FROM stg_dim_customer
ORDER BY customer_id;

SELECT TOP 5
    run_id,
    package_name,
    status,
    row_count_in,
    row_count_out,
    start_ts,
    end_ts
FROM etl_run_log
WHERE package_name = 'PKG_DIM_CUSTOMER'
ORDER BY run_id DESC;

SELECT COUNT(*) AS reject_count
FROM etl_reject_log
WHERE package_name = 'PKG_DIM_CUSTOMER';

-- QC-SS-04 : customer_id null en staging
SELECT COUNT(*) AS null_customer_id_stg
FROM stg_dim_customer
WHERE customer_id IS NULL;
