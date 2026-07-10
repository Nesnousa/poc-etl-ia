/* =====================================================================
   TEMPLATE GÉNÉRIQUE — Contrôles qualité d'une table de staging
   ---------------------------------------------------------------------
   Objectif : vérifier la qualité des données de n'importe quelle table
   de staging avant de la charger vers le modèle final (BI, entrepôt).

   Principe : chaque contrôle compare une VALEUR OBSERVÉE à un SEUIL,
   et renvoie PASS ou FAIL. Rien n'est modifié : on lit et on compte.

   Comment l'utiliser :
   1. Remplacer les variables { } par votre table et vos colonnes.
   2. Garder les contrôles pertinents, en supprimer ou en ajouter.
   3. Exécuter après chaque chargement (batch).

   Variables à remplacer :
     {table}         -> table à contrôler, ex. stg_dim_customer
     {cle}           -> clé métier, ex. customer_id
     {table_dim}     -> table dimension liée (contrôle de clés orphelines)
     {cle_dim}       -> clé dans la dimension liée
     {colonne_num}   -> colonne numérique à borner, ex. sales
     {min} / {max}   -> bornes valides, ex. 0 et 1000000
   ===================================================================== */

SET NOCOUNT ON;
DECLARE @batch_id INT = 1;   -- lot à contrôler

DECLARE @qc TABLE (
    check_id       NVARCHAR(20),
    check_name     NVARCHAR(200),
    observed_value NVARCHAR(50),
    threshold      NVARCHAR(50),
    status         NVARCHAR(10)
);

-- QC-01 : Volume — la table contient-elle des données ?
DECLARE @rows INT = (SELECT COUNT(*) FROM {table} WHERE batch_id = @batch_id);
INSERT INTO @qc VALUES ('QC-01', 'Volume {table}',
    CAST(@rows AS NVARCHAR(50)), '> 0',
    CASE WHEN @rows > 0 THEN 'PASS' ELSE 'FAIL' END);

-- QC-02 : Complétude — la clé métier est-elle toujours renseignée ?
DECLARE @null_key INT = (SELECT COUNT(*) FROM {table}
    WHERE batch_id = @batch_id AND {cle} IS NULL);
INSERT INTO @qc VALUES ('QC-02', '{cle} NULL dans {table}',
    CAST(@null_key AS NVARCHAR(50)), '= 0',
    CASE WHEN @null_key = 0 THEN 'PASS' ELSE 'FAIL' END);

-- QC-03 : Unicité — y a-t-il des doublons sur la clé métier ?
DECLARE @dup INT = (SELECT COUNT(*) FROM (
    SELECT {cle} FROM {table} WHERE batch_id = @batch_id
    GROUP BY {cle} HAVING COUNT(*) > 1) d);
INSERT INTO @qc VALUES ('QC-03', 'Doublons {cle} dans {table}',
    CAST(@dup AS NVARCHAR(50)), '= 0',
    CASE WHEN @dup = 0 THEN 'PASS' ELSE 'FAIL' END);

-- QC-04 : Intégrité référentielle — clés orphelines vers une dimension
DECLARE @orphan INT = (SELECT COUNT(*) FROM {table} f
    LEFT JOIN {table_dim} d ON f.{cle} = d.{cle_dim}
    WHERE f.batch_id = @batch_id AND d.{cle_dim} IS NULL);
INSERT INTO @qc VALUES ('QC-04', 'Clés orphelines {table} -> {table_dim}',
    CAST(@orphan AS NVARCHAR(50)), '= 0',
    CASE WHEN @orphan = 0 THEN 'PASS' ELSE 'FAIL' END);

-- QC-05 : Cohérence — valeur numérique dans un intervalle attendu
DECLARE @bad_val INT = (SELECT COUNT(*) FROM {table}
    WHERE batch_id = @batch_id AND {colonne_num} IS NOT NULL
      AND ({colonne_num} < {min} OR {colonne_num} > {max}));
INSERT INTO @qc VALUES ('QC-05', '{colonne_num} hors [{min}, {max}]',
    CAST(@bad_val AS NVARCHAR(50)), '= 0',
    CASE WHEN @bad_val = 0 THEN 'PASS' ELSE 'FAIL' END);

-- Résultat détaillé + synthèse PASS/FAIL
SELECT check_id, check_name, observed_value, threshold, status
FROM @qc ORDER BY check_id;

SELECT COUNT(*) AS total_checks,
       SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) AS passed,
       SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) AS failed
FROM @qc;
