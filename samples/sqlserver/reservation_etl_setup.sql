/* =====================================================================
   ETL RÉSERVATIONS — SETUP (source -> staging -> data warehouse)
   ---------------------------------------------------------------------
   Domaine d'exemple : réservations d'hôtel (différent de Superstore).
   Ce script crée TOUTES les couches du pipeline ETL :

     [SOURCE/LANDING]  raw_hotel_reservation      (copie brute type CSV)
            |
            v  (Package SSIS PKG_STG_RESERVATION  OU  usp_load_stg_hotel_reservation)
     [STAGING]         stg_hotel_reservation      (typé + traçabilité)
            |
            v  (procédures usp_load_dim_* / usp_load_fact_reservation)
     [DW en étoile]    dim_client / dim_chambre / dim_date / fact_reservation

   Il crée aussi la vue d'extraction utilisée par le package SSIS.
   Idempotent (réexécutable). Adapter les noms à votre domaine pour un
   autre projet (voir docs/05-cas-etude/14-etl-ssis-reservation.md).
   ===================================================================== */

USE POC_ETL_IA;
GO

-- Ordre de suppression : fait -> dimensions -> staging -> raw (clés étrangères)
IF OBJECT_ID('fact_reservation', 'U')      IS NOT NULL DROP TABLE fact_reservation;
IF OBJECT_ID('dim_client', 'U')            IS NOT NULL DROP TABLE dim_client;
IF OBJECT_ID('dim_chambre', 'U')           IS NOT NULL DROP TABLE dim_chambre;
IF OBJECT_ID('dim_date', 'U')              IS NOT NULL DROP TABLE dim_date;
IF OBJECT_ID('stg_hotel_reservation', 'U') IS NOT NULL DROP TABLE stg_hotel_reservation;
IF OBJECT_ID('vw_extract_hotel_reservation', 'V') IS NOT NULL DROP VIEW vw_extract_hotel_reservation;
IF OBJECT_ID('raw_hotel_reservation', 'U') IS NOT NULL DROP TABLE raw_hotel_reservation;
GO

/* =====================================================================
   1. SOURCE / LANDING — raw_hotel_reservation
   Copie brute (comme un CSV importé). Types larges, données imparfaites.
   ===================================================================== */
CREATE TABLE raw_hotel_reservation (
    reservation_id  NVARCHAR(50)   NULL,
    client_id       NVARCHAR(50)   NULL,
    client_nom      NVARCHAR(255)  NULL,
    client_ville    NVARCHAR(100)  NULL,
    client_pays     NVARCHAR(100)  NULL,
    chambre_id      NVARCHAR(50)   NULL,
    type_chambre    NVARCHAR(50)   NULL,
    capacite        NVARCHAR(20)   NULL,   -- brut (texte), converti en staging
    date_arrivee    NVARCHAR(20)   NULL,   -- brut (texte), converti en staging
    nb_nuits        NVARCHAR(20)   NULL,   -- brut (texte), converti en staging
    montant         NVARCHAR(30)   NULL,   -- brut (texte), converti en staging
    ingest_ts       DATETIME2      NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- Données d'exemple (dont 1 doublon RES-001 et des noms « sales »)
INSERT INTO raw_hotel_reservation
    (reservation_id, client_id, client_nom, client_ville, client_pays,
     chambre_id, type_chambre, capacite, date_arrivee, nb_nuits, montant)
VALUES
    ('RES-001', 'CLI-01', '  jean dupont ', 'Paris', 'France', 'CH-101', 'Standard', '2', '2026-01-10', '3', '300.00'),
    ('RES-001', 'CLI-01', '  jean dupont ', 'Paris', 'France', 'CH-101', 'Standard', '2', '2026-01-10', '3', '300.00'),
    ('RES-002', 'CLI-02', 'MARIE CURIE',    'Lyon',  'France', 'CH-202', 'Suite',    '4', '2026-01-12', '2', '500.00'),
    ('RES-003', 'CLI-03', 'ali ben salah',  'Tunis', 'Tunisie','CH-101', 'Standard', '2', '2026-01-15', '1', '100.00'),
    ('RES-004', 'CLI-01', '  jean dupont ', 'Paris', 'France', 'CH-303', 'Deluxe',   '3', '2026-01-20', '4', '600.00'),
    ('RES-005', 'CLI-04', 'Sofia Rossi',    'Rome',  'Italie', 'CH-202', 'Suite',    '4', '2026-01-22', '2', '480.00');
GO

/* Vue d'extraction pour le package SSIS (source -> staging).
   Elle type les colonnes et ajoute les métadonnées techniques. */
CREATE VIEW vw_extract_hotel_reservation
AS
SELECT
    CAST(1 AS INT)                       AS batch_id,
    CAST(N'DEMO_HOTEL' AS NVARCHAR(100)) AS source_system,
    reservation_id,
    client_id,
    client_nom,
    client_ville,
    client_pays,
    chambre_id,
    type_chambre,
    TRY_CAST(capacite AS INT)            AS capacite,
    TRY_CAST(date_arrivee AS DATE)       AS date_arrivee,
    TRY_CAST(nb_nuits AS INT)            AS nb_nuits,
    TRY_CAST(montant AS DECIMAL(18, 4))  AS montant,
    SYSUTCDATETIME()                     AS load_ts
FROM raw_hotel_reservation;
GO

/* =====================================================================
   2. STAGING — stg_hotel_reservation
   Une ligne = une ligne de réservation, typée, avec traçabilité ETL.
   (montant en DECIMAL(18,4) pour rester cohérent avec la métadonnée SSIS)
   ===================================================================== */
CREATE TABLE stg_hotel_reservation (
    batch_id        INT             NOT NULL,
    source_system   NVARCHAR(100)   NOT NULL,
    reservation_id  NVARCHAR(50)    NOT NULL,
    client_id       NVARCHAR(50)    NOT NULL,
    client_nom      NVARCHAR(255)   NULL,
    client_ville    NVARCHAR(100)   NULL,
    client_pays     NVARCHAR(100)   NULL,
    chambre_id      NVARCHAR(50)    NOT NULL,
    type_chambre    NVARCHAR(50)    NULL,
    capacite        INT             NULL,
    date_arrivee    DATE            NULL,
    nb_nuits        INT             NULL,
    montant         DECIMAL(18, 4)  NULL,
    load_ts         DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

CREATE INDEX IX_stg_hotel_reservation_batch ON stg_hotel_reservation (batch_id);
GO

/* =====================================================================
   3. DATA WAREHOUSE — schéma en étoile
   ===================================================================== */
CREATE TABLE dim_client (
    client_key       INT IDENTITY(1,1) NOT NULL,
    client_id        NVARCHAR(50)      NOT NULL,
    client_nom       NVARCHAR(255)     NULL,
    client_nom_clean NVARCHAR(255)     NULL,
    ville            NVARCHAR(100)     NULL,
    pays             NVARCHAR(100)     NULL,
    valid_from       DATETIME2         NOT NULL DEFAULT SYSUTCDATETIME(),
    valid_to         DATETIME2         NULL,
    is_current       BIT               NOT NULL DEFAULT 1,
    source_system    NVARCHAR(100)     NULL,
    dw_load_ts       DATETIME2         NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_dim_client PRIMARY KEY (client_key),
    CONSTRAINT UQ_dim_client_bk UNIQUE (client_id)
);
GO

CREATE TABLE dim_chambre (
    chambre_key    INT IDENTITY(1,1) NOT NULL,
    chambre_id     NVARCHAR(50)      NOT NULL,
    type_chambre   NVARCHAR(50)      NULL,
    capacite       INT               NULL,
    source_system  NVARCHAR(100)     NULL,
    dw_load_ts     DATETIME2         NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_dim_chambre PRIMARY KEY (chambre_key),
    CONSTRAINT UQ_dim_chambre_bk UNIQUE (chambre_id)
);
GO

CREATE TABLE dim_date (
    date_key       INT             NOT NULL,
    date_complete  DATE            NOT NULL,
    annee          INT             NULL,
    mois           INT             NULL,
    jour           INT             NULL,
    CONSTRAINT PK_dim_date PRIMARY KEY (date_key),
    CONSTRAINT UQ_dim_date UNIQUE (date_complete)
);
GO

CREATE TABLE fact_reservation (
    reservation_key  INT IDENTITY(1,1) NOT NULL,
    reservation_id   NVARCHAR(50)      NOT NULL,
    client_key       INT               NOT NULL,
    chambre_key      INT               NOT NULL,
    date_key         INT               NOT NULL,
    nb_nuits         INT               NULL,
    montant          DECIMAL(18, 2)    NULL,
    montant_par_nuit DECIMAL(18, 2)    NULL,
    dw_load_ts       DATETIME2         NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_fact_reservation PRIMARY KEY (reservation_key),
    CONSTRAINT FK_fact_res_client  FOREIGN KEY (client_key)  REFERENCES dim_client (client_key),
    CONSTRAINT FK_fact_res_chambre FOREIGN KEY (chambre_key) REFERENCES dim_chambre (chambre_key),
    CONSTRAINT FK_fact_res_date    FOREIGN KEY (date_key)    REFERENCES dim_date (date_key)
);
GO

CREATE INDEX IX_fact_reservation_client  ON fact_reservation (client_key);
CREATE INDEX IX_fact_reservation_chambre ON fact_reservation (chambre_key);
CREATE INDEX IX_fact_reservation_date    ON fact_reservation (date_key);
GO

/* =====================================================================
   4. VÉRIFICATION DU SETUP
   ===================================================================== */
SELECT 'raw_hotel_reservation' AS objet, COUNT(*) AS lignes FROM raw_hotel_reservation
UNION ALL SELECT 'stg_hotel_reservation', COUNT(*) FROM stg_hotel_reservation
UNION ALL SELECT 'dim_client',       COUNT(*) FROM dim_client
UNION ALL SELECT 'dim_chambre',      COUNT(*) FROM dim_chambre
UNION ALL SELECT 'dim_date',         COUNT(*) FROM dim_date
UNION ALL SELECT 'fact_reservation', COUNT(*) FROM fact_reservation;
GO

PRINT 'Setup ETL réservations terminé : raw alimenté (6 lignes), staging/DW créés et vides, en attente de l''ETL.';
GO
