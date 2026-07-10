/*
Reset avant execution du package SSIS
*/

TRUNCATE TABLE stg_sales_customer;
DELETE FROM etl_run_log;
DELETE FROM etl_error_log;
