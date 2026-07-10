/*
Validation post PKG_DIM_PRODUCT et PKG_FACT_SALES (7B-4)
*/
USE POC_ETL_IA;
GO

-- Dimensions prerequises
SELECT COUNT(*) AS stg_dim_customer_rows FROM stg_dim_customer;
SELECT COUNT(*) AS stg_dim_product_rows FROM stg_dim_product;

SELECT COUNT(DISTINCT product_id) AS distinct_products_raw
FROM raw_superstore
WHERE product_id IS NOT NULL;

SELECT COUNT(*) AS extract_product_view_rows FROM vw_extract_superstore_products;

SELECT TOP 5
    product_id,
    product_name,
    category,
    sub_category,
    load_ts
FROM stg_dim_product
ORDER BY product_id;

SELECT TOP 5
    run_id,
    package_name,
    status,
    row_count_in,
    row_count_out
FROM etl_run_log
WHERE package_name = 'PKG_DIM_PRODUCT'
ORDER BY run_id DESC;

SELECT COUNT(*) AS product_reject_count
FROM etl_reject_log
WHERE package_name = 'PKG_DIM_PRODUCT';

-- Fait ventes
SELECT COUNT(*) AS raw_rows FROM raw_superstore;
SELECT COUNT(*) AS stg_fact_sales_rows FROM stg_fact_sales;

SELECT TOP 5
    row_id,
    order_id,
    customer_id,
    product_id,
    sales,
    profit,
    margin_pct,
    load_ts
FROM stg_fact_sales
ORDER BY row_id;

SELECT TOP 5
    run_id,
    package_name,
    status,
    row_count_in,
    row_count_out
FROM etl_run_log
WHERE package_name = 'PKG_FACT_SALES'
ORDER BY run_id DESC;

SELECT COUNT(*) AS fact_reject_count
FROM etl_reject_log
WHERE package_name = 'PKG_FACT_SALES';

-- QC : cles etrangeres orphelines
SELECT COUNT(*) AS orphan_customer_keys
FROM stg_fact_sales f
LEFT JOIN stg_dim_customer c ON f.customer_id = c.customer_id AND c.batch_id = f.batch_id
WHERE c.customer_id IS NULL;

SELECT COUNT(*) AS orphan_product_keys
FROM stg_fact_sales f
LEFT JOIN stg_dim_product p ON f.product_id = p.product_id AND p.batch_id = f.batch_id
WHERE p.product_id IS NULL;
