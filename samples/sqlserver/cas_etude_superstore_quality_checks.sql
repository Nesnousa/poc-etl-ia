/*
Controles qualite Superstore - Phase 7B-5
Base : POC_ETL_IA
Executer apres : ingest Python (7B-2) + packages SSIS (7B-3, 7B-4)

Retourne un tableau synthese PASS/FAIL pour chaque controle QC-SS-xx.
*/
USE POC_ETL_IA;
GO

DECLARE @batch_id INT = 1;

DECLARE @qc TABLE (
    check_id        NVARCHAR(20)  NOT NULL,
    check_name      NVARCHAR(200) NOT NULL,
    observed_value  NVARCHAR(50)  NOT NULL,
    threshold       NVARCHAR(50)  NOT NULL,
    status          NVARCHAR(10)  NOT NULL
);

-- QC-SS-01 : volume raw
DECLARE @raw_rows INT = (SELECT COUNT(*) FROM raw_superstore);
INSERT INTO @qc VALUES (
    'QC-SS-01',
    'Volume raw_superstore',
    CAST(@raw_rows AS NVARCHAR(50)),
    '> 9000',
    CASE WHEN @raw_rows > 9000 THEN 'PASS' ELSE 'FAIL' END
);

-- QC-SS-02 : clients distincts en staging
DECLARE @cust_distinct INT = (
    SELECT COUNT(DISTINCT customer_id) FROM stg_dim_customer WHERE batch_id = @batch_id
);
INSERT INTO @qc VALUES (
    'QC-SS-02',
    'Clients distincts stg_dim_customer',
    CAST(@cust_distinct AS NVARCHAR(50)),
    '> 700',
    CASE WHEN @cust_distinct > 700 THEN 'PASS' ELSE 'FAIL' END
);

-- QC-SS-03 : produits distincts en staging
DECLARE @prod_distinct INT = (
    SELECT COUNT(DISTINCT product_id) FROM stg_dim_product WHERE batch_id = @batch_id
);
INSERT INTO @qc VALUES (
    'QC-SS-03',
    'Produits distincts stg_dim_product',
    CAST(@prod_distinct AS NVARCHAR(50)),
    '> 1800',
    CASE WHEN @prod_distinct > 1800 THEN 'PASS' ELSE 'FAIL' END
);

-- QC-SS-04 : customer_id null en staging client
DECLARE @null_cust INT = (
    SELECT COUNT(*) FROM stg_dim_customer WHERE batch_id = @batch_id AND customer_id IS NULL
);
INSERT INTO @qc VALUES (
    'QC-SS-04',
    'customer_id NULL en stg_dim_customer',
    CAST(@null_cust AS NVARCHAR(50)),
    '= 0',
    CASE WHEN @null_cust = 0 THEN 'PASS' ELSE 'FAIL' END
);

-- QC-SS-05 : product_id null en staging produit
DECLARE @null_prod INT = (
    SELECT COUNT(*) FROM stg_dim_product WHERE batch_id = @batch_id AND product_id IS NULL
);
INSERT INTO @qc VALUES (
    'QC-SS-05',
    'product_id NULL en stg_dim_product',
    CAST(@null_prod AS NVARCHAR(50)),
    '= 0',
    CASE WHEN @null_prod = 0 THEN 'PASS' ELSE 'FAIL' END
);

-- QC-SS-06 : lignes fait sans dimension (cles orphelines)
DECLARE @orphan_fact INT = (
    SELECT COUNT(*)
    FROM stg_fact_sales f
    LEFT JOIN stg_dim_customer c
        ON f.customer_id = c.customer_id AND c.batch_id = f.batch_id
    LEFT JOIN stg_dim_product p
        ON f.product_id = p.product_id AND p.batch_id = f.batch_id
    WHERE f.batch_id = @batch_id
      AND (c.customer_id IS NULL OR p.product_id IS NULL)
);
INSERT INTO @qc VALUES (
    'QC-SS-06',
    'Lignes fait sans dimension (lookup)',
    CAST(@orphan_fact AS NVARCHAR(50)),
    '= 0',
    CASE WHEN @orphan_fact = 0 THEN 'PASS' ELSE 'FAIL' END
);

-- QC-SS-07 : ventes negatives en staging fait
DECLARE @neg_sales INT = (
    SELECT COUNT(*) FROM stg_fact_sales
    WHERE batch_id = @batch_id AND sales IS NOT NULL AND sales < 0
);
INSERT INTO @qc VALUES (
    'QC-SS-07',
    'Ventes negatives stg_fact_sales',
    CAST(@neg_sales AS NVARCHAR(50)),
    '= 0',
    CASE WHEN @neg_sales = 0 THEN 'PASS' ELSE 'FAIL' END
);

-- QC-SS-08 : discount hors intervalle [0, 1]
DECLARE @bad_discount INT = (
    SELECT COUNT(*) FROM stg_fact_sales
    WHERE batch_id = @batch_id
      AND discount IS NOT NULL
      AND (discount < 0 OR discount > 1)
);
INSERT INTO @qc VALUES (
    'QC-SS-08',
    'Discount hors [0, 1] stg_fact_sales',
    CAST(@bad_discount AS NVARCHAR(50)),
    '= 0',
    CASE WHEN @bad_discount = 0 THEN 'PASS' ELSE 'FAIL' END
);

-- Controles complementaires (non bloquants, tracabilite)
DECLARE @dup_cust INT = (
    SELECT COUNT(*) FROM (
        SELECT customer_id FROM stg_dim_customer WHERE batch_id = @batch_id
        GROUP BY customer_id HAVING COUNT(*) > 1
    ) d
);
INSERT INTO @qc VALUES (
    'QC-SS-09',
    'Doublons customer_id stg_dim_customer',
    CAST(@dup_cust AS NVARCHAR(50)),
    '= 0',
    CASE WHEN @dup_cust = 0 THEN 'PASS' ELSE 'FAIL' END
);

DECLARE @dup_prod INT = (
    SELECT COUNT(*) FROM (
        SELECT product_id FROM stg_dim_product WHERE batch_id = @batch_id
        GROUP BY product_id HAVING COUNT(*) > 1
    ) d
);
INSERT INTO @qc VALUES (
    'QC-SS-10',
    'Doublons product_id stg_dim_product',
    CAST(@dup_prod AS NVARCHAR(50)),
    '= 0',
    CASE WHEN @dup_prod = 0 THEN 'PASS' ELSE 'FAIL' END
);

DECLARE @fact_rows INT = (SELECT COUNT(*) FROM stg_fact_sales WHERE batch_id = @batch_id);
INSERT INTO @qc VALUES (
    'QC-SS-11',
    'Reconciliation volume fait vs raw',
    CAST(@fact_rows AS NVARCHAR(50)) + ' / ' + CAST(@raw_rows AS NVARCHAR(50)),
    '= raw (lookup OK)',
    CASE WHEN @fact_rows = @raw_rows THEN 'PASS' ELSE 'WARN' END
);

DECLARE @pkg_ok INT = (
    SELECT COUNT(DISTINCT package_name)
    FROM etl_run_log
    WHERE package_name IN ('PKG_DIM_CUSTOMER', 'PKG_DIM_PRODUCT', 'PKG_FACT_SALES')
      AND status = 'SUCCESS'
);
INSERT INTO @qc VALUES (
    'QC-SS-12',
    'Packages SSIS en SUCCESS',
    CAST(@pkg_ok AS NVARCHAR(50)) + ' / 3',
    '= 3',
    CASE WHEN @pkg_ok = 3 THEN 'PASS' ELSE 'FAIL' END
);

-- =============================================================================
-- 1. Synthese controles
-- =============================================================================
SELECT
    check_id,
    check_name,
    observed_value,
    threshold,
    status
FROM @qc
ORDER BY check_id;

SELECT
    COUNT(*) AS total_checks,
    SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) AS passed,
    SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) AS failed,
    SUM(CASE WHEN status = 'WARN' THEN 1 ELSE 0 END) AS warnings
FROM @qc;

-- =============================================================================
-- 2. Volumes par couche
-- =============================================================================
SELECT 'raw_superstore' AS layer, COUNT(*) AS row_count FROM raw_superstore
UNION ALL
SELECT 'stg_dim_customer', COUNT(*) FROM stg_dim_customer WHERE batch_id = @batch_id
UNION ALL
SELECT 'stg_dim_product', COUNT(*) FROM stg_dim_product WHERE batch_id = @batch_id
UNION ALL
SELECT 'stg_fact_sales', COUNT(*) FROM stg_fact_sales WHERE batch_id = @batch_id
UNION ALL
SELECT 'etl_reject_log (superstore)', COUNT(*) FROM etl_reject_log
    WHERE package_name IN ('PKG_DIM_CUSTOMER', 'PKG_DIM_PRODUCT', 'PKG_FACT_SALES');

-- =============================================================================
-- 3. Derniers runs ETL
-- =============================================================================
SELECT
    run_id,
    package_name,
    status,
    row_count_in,
    row_count_out,
    start_ts,
    end_ts
FROM etl_run_log
WHERE package_name IN ('PKG_DIM_CUSTOMER', 'PKG_DIM_PRODUCT', 'PKG_FACT_SALES')
ORDER BY run_id DESC;

-- =============================================================================
-- 4. Echantillon margin_pct (verification regle metier)
-- =============================================================================
SELECT TOP 5
    row_id,
    sales,
    profit,
    margin_pct,
    CAST(CASE WHEN sales <> 0 THEN profit / sales ELSE NULL END AS DECIMAL(18, 4)) AS margin_pct_expected
FROM stg_fact_sales
WHERE batch_id = @batch_id AND sales IS NOT NULL AND sales <> 0
ORDER BY row_id;

GO
