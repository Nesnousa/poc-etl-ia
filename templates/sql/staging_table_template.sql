/* =====================================================================
   TEMPLATE GÉNÉRIQUE — Table de staging SQL Server
   ---------------------------------------------------------------------
   Objectif : créer une table de préparation (staging) pour n'importe
   quel domaine métier, avec les colonnes techniques de traçabilité.

   Comment l'utiliser :
   1. Remplacer les variables entre accolades { } par votre contexte.
   2. Remplacer le bloc "COLONNES MÉTIER" par les colonnes de votre source.
   3. Garder les colonnes techniques (batch_id, source_system, *_ts).

   Variables à remplacer :
     {table_staging}   -> nom de la table, ex. stg_dim_customer
     {colonne_cle}     -> clé métier principale, ex. customer_id
     {schema}          -> schéma SQL, ex. dbo
   ===================================================================== */

IF OBJECT_ID('{schema}.{table_staging}', 'U') IS NOT NULL
    DROP TABLE {schema}.{table_staging};
GO

CREATE TABLE {schema}.{table_staging} (
    -- ---- Colonnes techniques (à conserver sur toutes les tables) ----
    batch_id            INT             NOT NULL,   -- identifiant du lot ETL
    source_system       NVARCHAR(100)   NOT NULL,   -- système source, ex. KAGGLE
    source_extract_ts   DATETIME2       NULL,        -- horodatage d'extraction source
    load_ts             DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME(),

    -- ---- COLONNES MÉTIER (à adapter à votre source) ----------------
    {colonne_cle}       NVARCHAR(50)    NULL,        -- clé métier principale
    -- ex. attribut_1   NVARCHAR(255)   NULL,
    -- ex. attribut_2   NVARCHAR(100)   NULL,
    -- ex. montant      DECIMAL(18,2)   NULL,
    -- ex. quantite     INT             NULL,
    -- ex. date_evenement DATE          NULL
);
GO

-- Index sur le lot ETL (accélère les contrôles qualité par batch_id)
CREATE INDEX IX_{table_staging}_batch_id
    ON {schema}.{table_staging} (batch_id);
GO
