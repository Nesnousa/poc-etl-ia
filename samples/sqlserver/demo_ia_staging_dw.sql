/* =====================================================================
   EXEMPLE COMPLET — STAGING -> DATA WAREHOUSE (schéma en étoile)
   ---------------------------------------------------------------------
   Domaine d'exemple : RÉSERVATIONS D'HÔTEL (volontairement différent du
   cas Superstore, pour montrer que la démarche s'applique à n'importe
   quel projet).

   Ce que ce script illustre, de bout en bout :
     1) une table de STAGING (données préparées, clés métier, doublons possibles) ;
     2) un DATA WAREHOUSE en étoile :
          - 3 tables de DIMENSION (client, chambre, date) avec clé de substitution ;
          - 1 table de FAITS (réservations) avec les mesures ;
          - des RELATIONS (FOREIGN KEY) entre le fait et les dimensions ;
     3) le chargement staging -> DW (dédoublonnage, nettoyage, clés de substitution).

   Le script est AUTONOME (données d'exemple incluses) et idempotent
   (réexécutable). Adapter les noms d'objets et de colonnes à votre projet.

   Pour l'adapter à un AUTRE domaine : remplacer « hotel / client / chambre /
   reservation » par vos propres entités (ex. patient / acte / facture, etc.).
   ===================================================================== */

USE POC_ETL_IA;
GO

/* =====================================================================
   0. NETTOYAGE (idempotence) — on retire d'abord le fait, puis les
      dimensions (à cause des clés étrangères), puis le staging.
   ===================================================================== */
IF OBJECT_ID('fact_reservation_demo', 'U') IS NOT NULL DROP TABLE fact_reservation_demo;
IF OBJECT_ID('dim_client_demo', 'U')      IS NOT NULL DROP TABLE dim_client_demo;
IF OBJECT_ID('dim_chambre_demo', 'U')     IS NOT NULL DROP TABLE dim_chambre_demo;
IF OBJECT_ID('dim_date_demo', 'U')        IS NOT NULL DROP TABLE dim_date_demo;
IF OBJECT_ID('stg_hotel_reservation_demo', 'U') IS NOT NULL DROP TABLE stg_hotel_reservation_demo;
GO

/* =====================================================================
   1. TABLE DE STAGING — stg_hotel_reservation_demo
   ---------------------------------------------------------------------
   Une ligne = une ligne de réservation telle que préparée depuis la
   source. Contient les clés métier et des colonnes techniques. Les
   données peuvent être imparfaites (doublons, casse/espaces).
   ===================================================================== */
CREATE TABLE stg_hotel_reservation_demo (
    -- Colonnes techniques (traçabilité ETL)
    batch_id        INT             NOT NULL,
    source_system   NVARCHAR(100)   NOT NULL,
    load_ts         DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME(),

    -- Colonnes métier (clés naturelles + attributs)
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
    montant         DECIMAL(18, 2)  NULL
);
GO

CREATE INDEX IX_stg_hotel_reservation_demo_batch ON stg_hotel_reservation_demo (batch_id);
GO

/* =====================================================================
   2. TABLES DE DIMENSION (DW)
   ---------------------------------------------------------------------
   Chaque dimension possède une CLÉ DE SUBSTITUTION (surrogate key)
   auto-incrémentée, stable et indépendante de la source, plus la clé
   métier en contrainte UNIQUE.
   ===================================================================== */

-- 2.1 Dimension CLIENT
CREATE TABLE dim_client_demo (
    client_key      INT IDENTITY(1,1) NOT NULL,
    client_id       NVARCHAR(50)      NOT NULL,
    client_nom      NVARCHAR(255)     NULL,
    client_nom_clean NVARCHAR(255)    NULL,
    ville           NVARCHAR(100)     NULL,
    pays            NVARCHAR(100)     NULL,
    -- Historisation (Slowly Changing Dimension)
    valid_from      DATETIME2         NOT NULL DEFAULT SYSUTCDATETIME(),
    valid_to        DATETIME2         NULL,
    is_current      BIT               NOT NULL DEFAULT 1,
    -- Audit DW
    source_system   NVARCHAR(100)     NULL,
    dw_load_ts      DATETIME2         NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_dim_client_demo PRIMARY KEY (client_key),
    CONSTRAINT UQ_dim_client_demo_bk UNIQUE (client_id)
);
GO

-- 2.2 Dimension CHAMBRE
CREATE TABLE dim_chambre_demo (
    chambre_key     INT IDENTITY(1,1) NOT NULL,
    chambre_id      NVARCHAR(50)      NOT NULL,
    type_chambre    NVARCHAR(50)      NULL,
    capacite        INT               NULL,
    source_system   NVARCHAR(100)     NULL,
    dw_load_ts      DATETIME2         NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_dim_chambre_demo PRIMARY KEY (chambre_key),
    CONSTRAINT UQ_dim_chambre_demo_bk UNIQUE (chambre_id)
);
GO

-- 2.3 Dimension DATE (calendrier simplifié)
CREATE TABLE dim_date_demo (
    date_key        INT             NOT NULL,   -- format AAAAMMJJ
    date_complete   DATE            NOT NULL,
    annee           INT             NULL,
    mois            INT             NULL,
    jour            INT             NULL,
    CONSTRAINT PK_dim_date_demo PRIMARY KEY (date_key),
    CONSTRAINT UQ_dim_date_demo UNIQUE (date_complete)
);
GO

/* =====================================================================
   3. TABLE DE FAITS (DW) — fact_reservation_demo
   ---------------------------------------------------------------------
   Une ligne = une réservation. Contient les MESURES (nb_nuits, montant)
   et des CLÉS ÉTRANGÈRES vers les dimensions (relations du schéma étoile).
   ===================================================================== */
CREATE TABLE fact_reservation_demo (
    reservation_key   INT IDENTITY(1,1) NOT NULL,
    reservation_id    NVARCHAR(50)      NOT NULL,
    client_key        INT               NOT NULL,
    chambre_key       INT               NOT NULL,
    date_key          INT               NOT NULL,
    nb_nuits          INT               NULL,
    montant           DECIMAL(18, 2)    NULL,
    montant_par_nuit  DECIMAL(18, 2)    NULL,
    dw_load_ts        DATETIME2         NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT PK_fact_reservation_demo PRIMARY KEY (reservation_key),
    -- RELATIONS (schéma en étoile) : le fait référence chaque dimension
    CONSTRAINT FK_fact_client  FOREIGN KEY (client_key)  REFERENCES dim_client_demo (client_key),
    CONSTRAINT FK_fact_chambre FOREIGN KEY (chambre_key) REFERENCES dim_chambre_demo (chambre_key),
    CONSTRAINT FK_fact_date    FOREIGN KEY (date_key)    REFERENCES dim_date_demo (date_key)
);
GO

/* =====================================================================
   4. DONNÉES D'EXEMPLE EN STAGING
   ---------------------------------------------------------------------
   On insère un DOUBLON (RES-001 deux fois) et des noms « sales »
   (espaces / casse) pour illustrer le nettoyage/dédoublonnage.
   ===================================================================== */
INSERT INTO stg_hotel_reservation_demo
    (batch_id, source_system, reservation_id, client_id, client_nom, client_ville, client_pays,
     chambre_id, type_chambre, capacite, date_arrivee, nb_nuits, montant)
VALUES
    (1, 'DEMO', 'RES-001', 'CLI-01', '  jean dupont ', 'Paris', 'France', 'CH-101', 'Standard', 2, '2026-01-10', 3, 300.00),
    (1, 'DEMO', 'RES-001', 'CLI-01', '  jean dupont ', 'Paris', 'France', 'CH-101', 'Standard', 2, '2026-01-10', 3, 300.00), -- doublon
    (1, 'DEMO', 'RES-002', 'CLI-02', 'MARIE CURIE',    'Lyon',  'France', 'CH-202', 'Suite',    4, '2026-01-12', 2, 500.00),
    (1, 'DEMO', 'RES-003', 'CLI-03', 'ali ben salah',  'Tunis', 'Tunisie','CH-101', 'Standard', 2, '2026-01-15', 1, 100.00),
    (1, 'DEMO', 'RES-004', 'CLI-01', '  jean dupont ', 'Paris', 'France', 'CH-303', 'Deluxe',   3, '2026-01-20', 4, 600.00);
GO

/* =====================================================================
   5. CHARGEMENT STAGING -> DIMENSIONS
   ===================================================================== */

-- 5.1 dim_client : une ligne par client_id, nom nettoyé (TRIM + casse)
WITH client_dedup AS (
    SELECT client_id, client_nom, LTRIM(RTRIM(client_nom)) AS nom_trim,
           client_ville, client_pays, source_system,
           ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY load_ts DESC) AS rn
    FROM stg_hotel_reservation_demo
    WHERE batch_id = 1
)
INSERT INTO dim_client_demo (client_id, client_nom, client_nom_clean, ville, pays, source_system)
SELECT client_id, client_nom,
       UPPER(LEFT(nom_trim, 1)) + LOWER(SUBSTRING(nom_trim, 2, 255)),
       client_ville, client_pays, source_system
FROM client_dedup
WHERE rn = 1;
GO

-- 5.2 dim_chambre : une ligne par chambre_id
WITH chambre_dedup AS (
    SELECT chambre_id, type_chambre, capacite, source_system,
           ROW_NUMBER() OVER (PARTITION BY chambre_id ORDER BY load_ts DESC) AS rn
    FROM stg_hotel_reservation_demo
    WHERE batch_id = 1
)
INSERT INTO dim_chambre_demo (chambre_id, type_chambre, capacite, source_system)
SELECT chambre_id, type_chambre, capacite, source_system
FROM chambre_dedup
WHERE rn = 1;
GO

-- 5.3 dim_date : une ligne par date d'arrivée distincte
INSERT INTO dim_date_demo (date_key, date_complete, annee, mois, jour)
SELECT DISTINCT
    YEAR(date_arrivee) * 10000 + MONTH(date_arrivee) * 100 + DAY(date_arrivee),
    date_arrivee, YEAR(date_arrivee), MONTH(date_arrivee), DAY(date_arrivee)
FROM stg_hotel_reservation_demo
WHERE batch_id = 1 AND date_arrivee IS NOT NULL;
GO

/* =====================================================================
   6. CHARGEMENT STAGING -> FAIT
   ---------------------------------------------------------------------
   On dédoublonne les réservations, puis on récupère les clés de
   substitution par jointure sur les dimensions (résolution des lookups).
   ===================================================================== */
WITH resa_dedup AS (
    SELECT reservation_id, client_id, chambre_id, date_arrivee, nb_nuits, montant,
           ROW_NUMBER() OVER (PARTITION BY reservation_id ORDER BY load_ts DESC) AS rn
    FROM stg_hotel_reservation_demo
    WHERE batch_id = 1
)
INSERT INTO fact_reservation_demo
    (reservation_id, client_key, chambre_key, date_key, nb_nuits, montant, montant_par_nuit)
SELECT
    r.reservation_id,
    c.client_key,
    ch.chambre_key,
    d.date_key,
    r.nb_nuits,
    r.montant,
    CAST(r.montant / NULLIF(r.nb_nuits, 0) AS DECIMAL(18, 2))
FROM resa_dedup r
JOIN dim_client_demo  c  ON r.client_id  = c.client_id
JOIN dim_chambre_demo ch ON r.chambre_id = ch.chambre_id
JOIN dim_date_demo    d  ON r.date_arrivee = d.date_complete
WHERE r.rn = 1;
GO

/* =====================================================================
   7. VÉRIFICATION
   ===================================================================== */
SELECT 'stg_hotel_reservation_demo' AS objet, COUNT(*) AS lignes FROM stg_hotel_reservation_demo
UNION ALL SELECT 'dim_client_demo',      COUNT(*) FROM dim_client_demo
UNION ALL SELECT 'dim_chambre_demo',     COUNT(*) FROM dim_chambre_demo
UNION ALL SELECT 'dim_date_demo',        COUNT(*) FROM dim_date_demo
UNION ALL SELECT 'fact_reservation_demo', COUNT(*) FROM fact_reservation_demo;
GO

-- Aperçu analytique : le fait relié à ses dimensions (schéma en étoile)
SELECT
    f.reservation_id,
    c.client_nom_clean AS client,
    c.ville,
    ch.type_chambre,
    d.date_complete    AS date_arrivee,
    f.nb_nuits,
    f.montant,
    f.montant_par_nuit
FROM fact_reservation_demo f
JOIN dim_client_demo  c  ON f.client_key  = c.client_key
JOIN dim_chambre_demo ch ON f.chambre_key = ch.chambre_key
JOIN dim_date_demo    d  ON f.date_key    = d.date_key
ORDER BY f.reservation_id;
GO

PRINT 'Exemple staging -> DW terminé : 5 lignes staging (dont 1 doublon) -> 3 clients, 3 chambres, 4 dates, 4 réservations en fait.';
GO

/* =====================================================================
   8. NETTOYAGE OPTIONNEL (décommenter pour tout supprimer)
   ---------------------------------------------------------------------
   IF OBJECT_ID('fact_reservation_demo', 'U') IS NOT NULL DROP TABLE fact_reservation_demo;
   IF OBJECT_ID('dim_client_demo', 'U')      IS NOT NULL DROP TABLE dim_client_demo;
   IF OBJECT_ID('dim_chambre_demo', 'U')     IS NOT NULL DROP TABLE dim_chambre_demo;
   IF OBJECT_ID('dim_date_demo', 'U')        IS NOT NULL DROP TABLE dim_date_demo;
   IF OBJECT_ID('stg_hotel_reservation_demo', 'U') IS NOT NULL DROP TABLE stg_hotel_reservation_demo;
   ===================================================================== */
