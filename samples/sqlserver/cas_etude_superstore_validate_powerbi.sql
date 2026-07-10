/*
Validation croisee Power BI vs SQL — Phase 9 Superstore
Executer dans SSMS et comparer avec les cartes / visuels PBI.
*/
USE POC_ETL_IA;
GO

DECLARE @batch_id INT = 1;

-- Totaux a reporter dans Power BI (cartes KPI)
SELECT
    SUM(sales) AS total_sales_sql,
    SUM(profit) AS total_profit_sql,
    SUM(quantity) AS total_quantity_sql,
    COUNT(DISTINCT order_id) AS distinct_orders_sql,
    AVG(discount) AS avg_discount_sql,
    CASE
        WHEN SUM(sales) <> 0 THEN SUM(profit) / SUM(sales)
        ELSE NULL
    END AS margin_pct_sql
FROM stg_fact_sales
WHERE batch_id = @batch_id;

-- Volumes
SELECT COUNT(*) AS fact_rows FROM stg_fact_sales WHERE batch_id = @batch_id;
SELECT COUNT(*) AS customer_rows FROM stg_dim_customer WHERE batch_id = @batch_id;
SELECT COUNT(*) AS product_rows FROM stg_dim_product WHERE batch_id = @batch_id;

-- Ventes par region (graphique barres PBI)
SELECT
    c.region,
    SUM(f.sales) AS sales_by_region,
    SUM(f.profit) AS profit_by_region
FROM stg_fact_sales f
INNER JOIN stg_dim_customer c
    ON f.customer_id = c.customer_id AND c.batch_id = f.batch_id
WHERE f.batch_id = @batch_id
GROUP BY c.region
ORDER BY sales_by_region DESC;

-- Profit par categorie produit (2e graphique)
SELECT
    p.category,
    SUM(f.sales) AS sales_by_category,
    SUM(f.profit) AS profit_by_category
FROM stg_fact_sales f
INNER JOIN stg_dim_product p
    ON f.product_id = p.product_id AND p.batch_id = f.batch_id
WHERE f.batch_id = @batch_id
GROUP BY p.category
ORDER BY profit_by_category DESC;

GO
