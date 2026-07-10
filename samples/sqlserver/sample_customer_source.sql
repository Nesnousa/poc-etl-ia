/*
Jeu d'exemple pour le cas d'etude ETL client
*/

IF OBJECT_ID('src_customer', 'U') IS NOT NULL
    DROP TABLE src_customer;
GO

CREATE TABLE src_customer (
    customer_id     INT             NOT NULL,
    customer_code   NVARCHAR(50)    NOT NULL,
    customer_name   NVARCHAR(255)   NOT NULL,
    country_code    NVARCHAR(10)    NULL,
    email_address   NVARCHAR(255)   NULL,
    updated_at      DATETIME2       NOT NULL
);
GO

INSERT INTO src_customer (customer_id, customer_code, customer_name, country_code, email_address, updated_at)
VALUES
    (1, 'C001', 'Alpha Retail', 'FR', 'contact@alpha.fr', '2026-06-01T08:00:00'),
    (2, 'C002', 'Beta Services', 'DE', 'info@beta.de', '2026-06-01T08:00:00'),
    (3, 'C003', 'Gamma Corp', 'US', NULL, '2026-06-01T08:00:00'),
    (4, 'C001', 'Alpha Retail Duplicate', 'FR', 'dup@alpha.fr', '2026-06-01T08:00:00');
GO
