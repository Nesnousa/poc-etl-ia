"""Exécution et diagnostic des contrôles qualité Superstore pour Streamlit (7B-5)."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

try:
    import pyodbc
except ImportError:  # environnement cloud sans driver SQL Server (démo en ligne)
    pyodbc = None

_NO_PYODBC_MSG = (
    "Le connecteur SQL Server (pyodbc) n'est pas disponible dans cet environnement. "
    "Cette page fonctionne en local, connectée à votre SQL Server. "
    "Utilisez le mode « Démonstration » pour visualiser un exemple."
)

BATCH_ID = 1

QC_BATCH_SQL = """
SET NOCOUNT ON;

DECLARE @batch_id INT = 1;
DECLARE @qc TABLE (
    check_id NVARCHAR(20) NOT NULL,
    check_name NVARCHAR(200) NOT NULL,
    observed_value NVARCHAR(50) NOT NULL,
    threshold NVARCHAR(50) NOT NULL,
    status NVARCHAR(10) NOT NULL
);

DECLARE @raw_rows INT = (SELECT COUNT(*) FROM raw_superstore);
INSERT INTO @qc VALUES ('QC-SS-01', 'Volume raw_superstore', CAST(@raw_rows AS NVARCHAR(50)), '> 9000', CASE WHEN @raw_rows > 9000 THEN 'PASS' ELSE 'FAIL' END);

DECLARE @cust_distinct INT = (SELECT COUNT(DISTINCT customer_id) FROM stg_dim_customer WHERE batch_id = @batch_id);
INSERT INTO @qc VALUES ('QC-SS-02', 'Clients distincts stg_dim_customer', CAST(@cust_distinct AS NVARCHAR(50)), '> 700', CASE WHEN @cust_distinct > 700 THEN 'PASS' ELSE 'FAIL' END);

DECLARE @prod_distinct INT = (SELECT COUNT(DISTINCT product_id) FROM stg_dim_product WHERE batch_id = @batch_id);
INSERT INTO @qc VALUES ('QC-SS-03', 'Produits distincts stg_dim_product', CAST(@prod_distinct AS NVARCHAR(50)), '> 1800', CASE WHEN @prod_distinct > 1800 THEN 'PASS' ELSE 'FAIL' END);

DECLARE @null_cust INT = (SELECT COUNT(*) FROM stg_dim_customer WHERE batch_id = @batch_id AND customer_id IS NULL);
INSERT INTO @qc VALUES ('QC-SS-04', 'customer_id NULL dans stg_dim_customer', CAST(@null_cust AS NVARCHAR(50)), '= 0', CASE WHEN @null_cust = 0 THEN 'PASS' ELSE 'FAIL' END);

DECLARE @null_prod INT = (SELECT COUNT(*) FROM stg_dim_product WHERE batch_id = @batch_id AND product_id IS NULL);
INSERT INTO @qc VALUES ('QC-SS-05', 'product_id NULL dans stg_dim_product', CAST(@null_prod AS NVARCHAR(50)), '= 0', CASE WHEN @null_prod = 0 THEN 'PASS' ELSE 'FAIL' END);

DECLARE @orphan_fact INT = (
    SELECT COUNT(*)
    FROM stg_fact_sales f
    LEFT JOIN stg_dim_customer c ON f.customer_id = c.customer_id AND c.batch_id = f.batch_id
    LEFT JOIN stg_dim_product p ON f.product_id = p.product_id AND p.batch_id = f.batch_id
    WHERE f.batch_id = @batch_id AND (c.customer_id IS NULL OR p.product_id IS NULL)
);
INSERT INTO @qc VALUES ('QC-SS-06', 'Lignes de fait sans dimension (lookup)', CAST(@orphan_fact AS NVARCHAR(50)), '= 0', CASE WHEN @orphan_fact = 0 THEN 'PASS' ELSE 'FAIL' END);

DECLARE @neg_sales INT = (SELECT COUNT(*) FROM stg_fact_sales WHERE batch_id = @batch_id AND sales IS NOT NULL AND sales < 0);
INSERT INTO @qc VALUES ('QC-SS-07', 'Ventes négatives dans stg_fact_sales', CAST(@neg_sales AS NVARCHAR(50)), '= 0', CASE WHEN @neg_sales = 0 THEN 'PASS' ELSE 'FAIL' END);

DECLARE @bad_discount INT = (SELECT COUNT(*) FROM stg_fact_sales WHERE batch_id = @batch_id AND discount IS NOT NULL AND (discount < 0 OR discount > 1));
INSERT INTO @qc VALUES ('QC-SS-08', 'Discount hors [0, 1] dans stg_fact_sales', CAST(@bad_discount AS NVARCHAR(50)), '= 0', CASE WHEN @bad_discount = 0 THEN 'PASS' ELSE 'FAIL' END);

DECLARE @dup_cust INT = (SELECT COUNT(*) FROM (SELECT customer_id FROM stg_dim_customer WHERE batch_id = @batch_id GROUP BY customer_id HAVING COUNT(*) > 1) d);
INSERT INTO @qc VALUES ('QC-SS-09', 'Doublons customer_id dans stg_dim_customer', CAST(@dup_cust AS NVARCHAR(50)), '= 0', CASE WHEN @dup_cust = 0 THEN 'PASS' ELSE 'FAIL' END);

DECLARE @dup_prod INT = (SELECT COUNT(*) FROM (SELECT product_id FROM stg_dim_product WHERE batch_id = @batch_id GROUP BY product_id HAVING COUNT(*) > 1) d);
INSERT INTO @qc VALUES ('QC-SS-10', 'Doublons product_id dans stg_dim_product', CAST(@dup_prod AS NVARCHAR(50)), '= 0', CASE WHEN @dup_prod = 0 THEN 'PASS' ELSE 'FAIL' END);

DECLARE @fact_rows INT = (SELECT COUNT(*) FROM stg_fact_sales WHERE batch_id = @batch_id);
INSERT INTO @qc VALUES ('QC-SS-11', 'Réconciliation volume fait vs raw', CAST(@fact_rows AS NVARCHAR(50)) + ' / ' + CAST(@raw_rows AS NVARCHAR(50)), '= raw (lookup OK)', CASE WHEN @fact_rows = @raw_rows THEN 'PASS' ELSE 'WARN' END);

DECLARE @pkg_ok INT = (
    SELECT COUNT(DISTINCT package_name) FROM etl_run_log
    WHERE package_name IN ('PKG_DIM_CUSTOMER', 'PKG_DIM_PRODUCT', 'PKG_FACT_SALES') AND status = 'SUCCESS'
);
INSERT INTO @qc VALUES ('QC-SS-12', 'Packages SSIS en SUCCESS', CAST(@pkg_ok AS NVARCHAR(50)) + ' / 3', '= 3', CASE WHEN @pkg_ok = 3 THEN 'PASS' ELSE 'FAIL' END);

SELECT check_id, check_name, observed_value, threshold, status FROM @qc ORDER BY check_id;
SELECT COUNT(*) AS total_checks, SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END) AS passed, SUM(CASE WHEN status = 'FAIL' THEN 1 ELSE 0 END) AS failed, SUM(CASE WHEN status = 'WARN' THEN 1 ELSE 0 END) AS warnings FROM @qc;
"""


@dataclass(frozen=True)
class QcGuide:
    pipeline_step: str
    table_or_package: str
    cause: str
    fix_steps: list[str]
    diagnostic_sql: str
    reset_script: str | None = None


QC_GUIDES: dict[str, QcGuide] = {
    "QC-SS-01": QcGuide(
        pipeline_step="7B-2 — Ingestion Python",
        table_or_package="raw_superstore",
        cause="La table d'atterrissage (landing) est vide ou sous-dimensionnée : le CSV n'a pas été chargé correctement.",
        fix_steps=[
            "Vérifier que le fichier CSV existe bien dans `samples/data/superstore/`.",
            "Exécuter : `python samples/python/ingest_superstore_to_sql.py`.",
            "Contrôler dans SSMS : `SELECT COUNT(*) FROM raw_superstore;`",
        ],
        diagnostic_sql="SELECT TOP 10 * FROM raw_superstore ORDER BY row_id;",
        reset_script=None,
    ),
    "QC-SS-02": QcGuide(
        pipeline_step="7B-3 — PKG_DIM_CUSTOMER",
        table_or_package="stg_dim_customer",
        cause="Le package client n'a pas chargé suffisamment de lignes, ou n'a pas été exécuté.",
        fix_steps=[
            "Exécuter `samples/sqlserver/cas_etude_superstore_reset_stg_customer.sql`.",
            "Lancer `PKG_DIM_CUSTOMER` dans Visual Studio.",
            "Vérifier `etl_run_log` : statut = SUCCESS, row_count_out proche de 793.",
        ],
        diagnostic_sql=(
            "SELECT COUNT(*) AS stg_rows, COUNT(DISTINCT customer_id) AS distinct_ids "
            "FROM stg_dim_customer WHERE batch_id = 1;"
        ),
        reset_script="samples/sqlserver/cas_etude_superstore_reset_stg_customer.sql",
    ),
    "QC-SS-03": QcGuide(
        pipeline_step="7B-4 — PKG_DIM_PRODUCT",
        table_or_package="stg_dim_product",
        cause="Le package produit n'a pas chargé suffisamment de lignes, ou n'a pas été exécuté.",
        fix_steps=[
            "Exécuter `samples/sqlserver/cas_etude_superstore_reset_stg_product.sql`.",
            "Lancer `PKG_DIM_PRODUCT` dans Visual Studio.",
            "Vérifier `etl_run_log` : statut = SUCCESS, row_count_out proche de 1862.",
        ],
        diagnostic_sql=(
            "SELECT COUNT(*) AS stg_rows, COUNT(DISTINCT product_id) AS distinct_ids "
            "FROM stg_dim_product WHERE batch_id = 1;"
        ),
        reset_script="samples/sqlserver/cas_etude_superstore_reset_stg_product.sql",
    ),
    "QC-SS-04": QcGuide(
        pipeline_step="7B-3 — PKG_DIM_CUSTOMER",
        table_or_package="stg_dim_customer",
        cause="Des lignes avec un customer_id NULL ont été chargées (filtre SSIS insuffisant).",
        fix_steps=[
            "Identifier les lignes concernées ci-dessous.",
            "Corriger la source ou le filtre SQL du package (`HAVING customer_id IS NOT NULL`).",
            "Réinitialiser puis réexécuter PKG_DIM_CUSTOMER.",
        ],
        diagnostic_sql=(
            "SELECT TOP 20 customer_id, customer_name, segment, load_ts "
            "FROM stg_dim_customer WHERE batch_id = 1 AND customer_id IS NULL;"
        ),
        reset_script="samples/sqlserver/cas_etude_superstore_reset_stg_customer.sql",
    ),
    "QC-SS-05": QcGuide(
        pipeline_step="7B-4 — PKG_DIM_PRODUCT",
        table_or_package="stg_dim_product",
        cause="Des lignes avec un product_id NULL ont été chargées.",
        fix_steps=[
            "Identifier les lignes concernées ci-dessous.",
            "Vérifier la clause `HAVING` du package produit.",
            "Réinitialiser puis réexécuter PKG_DIM_PRODUCT.",
        ],
        diagnostic_sql=(
            "SELECT TOP 20 product_id, product_name, category, load_ts "
            "FROM stg_dim_product WHERE batch_id = 1 AND product_id IS NULL;"
        ),
        reset_script="samples/sqlserver/cas_etude_superstore_reset_stg_product.sql",
    ),
    "QC-SS-06": QcGuide(
        pipeline_step="7B-4 — PKG_FACT_SALES (lookup dimensions)",
        table_or_package="stg_fact_sales",
        cause="Des ventes référencent un client ou un produit absent des dimensions en staging.",
        fix_steps=[
            "Vérifier que PKG_DIM_CUSTOMER et PKG_DIM_PRODUCT sont bien en SUCCESS.",
            "Identifier les clés orphelines avec la requête ci-dessous.",
            "Réinitialiser le fait : `cas_etude_superstore_reset_stg_fact.sql`.",
            "Réexécuter dans l'ordre : Client → Produit → Fait.",
        ],
        diagnostic_sql="""
SELECT TOP 20
    f.row_id,
    f.order_id,
    f.customer_id,
    f.product_id,
    CASE WHEN c.customer_id IS NULL THEN 'MANQUANT' ELSE 'OK' END AS dim_customer,
    CASE WHEN p.product_id IS NULL THEN 'MANQUANT' ELSE 'OK' END AS dim_product
FROM stg_fact_sales f
LEFT JOIN stg_dim_customer c ON f.customer_id = c.customer_id AND c.batch_id = f.batch_id
LEFT JOIN stg_dim_product p ON f.product_id = p.product_id AND p.batch_id = f.batch_id
WHERE f.batch_id = 1 AND (c.customer_id IS NULL OR p.product_id IS NULL);
""",
        reset_script="samples/sqlserver/cas_etude_superstore_reset_stg_fact.sql",
    ),
    "QC-SS-07": QcGuide(
        pipeline_step="7B-4 — PKG_FACT_SALES",
        table_or_package="stg_fact_sales",
        cause="Des lignes ont un montant de ventes (sales) négatif — anomalie métier ou source.",
        fix_steps=[
            "Examiner les lignes concernées ci-dessous.",
            "Vérifier la source `raw_superstore` pour les mêmes row_id.",
            "Ajouter un filtre ou une règle de rejet dans PKG_FACT_SALES si nécessaire.",
        ],
        diagnostic_sql=(
            "SELECT TOP 20 row_id, order_id, customer_id, product_id, sales, profit "
            "FROM stg_fact_sales WHERE batch_id = 1 AND sales < 0 ORDER BY row_id;"
        ),
        reset_script="samples/sqlserver/cas_etude_superstore_reset_stg_fact.sql",
    ),
    "QC-SS-08": QcGuide(
        pipeline_step="7B-4 — PKG_FACT_SALES",
        table_or_package="stg_fact_sales",
        cause="Des valeurs de discount sont hors de l'intervalle [0, 1].",
        fix_steps=[
            "Examiner les lignes concernées ci-dessous.",
            "Vérifier si le CSV source contient des valeurs aberrantes.",
            "Ajouter une règle de rejet dans le bloc SQL_LogRejects du package fait.",
        ],
        diagnostic_sql=(
            "SELECT TOP 20 row_id, order_id, discount, sales, profit "
            "FROM stg_fact_sales WHERE batch_id = 1 AND (discount < 0 OR discount > 1) ORDER BY row_id;"
        ),
        reset_script="samples/sqlserver/cas_etude_superstore_reset_stg_fact.sql",
    ),
    "QC-SS-09": QcGuide(
        pipeline_step="7B-3 — PKG_DIM_CUSTOMER (dédoublonnage)",
        table_or_package="stg_dim_customer",
        cause="Le dédoublonnage par customer_id a échoué : plusieurs lignes existent pour la même clé.",
        fix_steps=[
            "Lister les doublons avec la requête ci-dessous.",
            "Vérifier la clause GROUP BY dans la source SQL du package.",
            "Réinitialiser puis réexécuter PKG_DIM_CUSTOMER.",
        ],
        diagnostic_sql="""
SELECT customer_id, COUNT(*) AS nb_lignes
FROM stg_dim_customer WHERE batch_id = 1
GROUP BY customer_id HAVING COUNT(*) > 1;
""",
        reset_script="samples/sqlserver/cas_etude_superstore_reset_stg_customer.sql",
    ),
    "QC-SS-10": QcGuide(
        pipeline_step="7B-4 — PKG_DIM_PRODUCT (dédoublonnage)",
        table_or_package="stg_dim_product",
        cause="Plusieurs lignes existent pour le même product_id.",
        fix_steps=[
            "Lister les doublons avec la requête ci-dessous.",
            "Vérifier la clause GROUP BY dans PKG_DIM_PRODUCT.",
            "Réinitialiser puis réexécuter PKG_DIM_PRODUCT.",
        ],
        diagnostic_sql="""
SELECT product_id, COUNT(*) AS nb_lignes
FROM stg_dim_product WHERE batch_id = 1
GROUP BY product_id HAVING COUNT(*) > 1;
""",
        reset_script="samples/sqlserver/cas_etude_superstore_reset_stg_product.sql",
    ),
    "QC-SS-11": QcGuide(
        pipeline_step="7B-4 — PKG_FACT_SALES (réconciliation)",
        table_or_package="stg_fact_sales vs raw_superstore",
        cause="Le nombre de lignes en fait ne correspond pas au volume brut (rejets de lookup ou filtre).",
        fix_steps=[
            "Comparer les volumes raw vs fait avec la requête ci-dessous.",
            "Vérifier `etl_reject_log` pour le package PKG_FACT_SALES.",
            "S'assurer que les dimensions sont chargées avant le fait.",
            "Réexécuter PKG_FACT_SALES après correction.",
        ],
        diagnostic_sql="""
SELECT 'raw_superstore' AS source, COUNT(*) AS nb FROM raw_superstore
UNION ALL
SELECT 'stg_fact_sales', COUNT(*) FROM stg_fact_sales WHERE batch_id = 1
UNION ALL
SELECT 'rejets PKG_FACT_SALES', COUNT(*) FROM etl_reject_log WHERE package_name = 'PKG_FACT_SALES';
""",
        reset_script="samples/sqlserver/cas_etude_superstore_reset_stg_fact.sql",
    ),
    "QC-SS-12": QcGuide(
        pipeline_step="7B-3 / 7B-4 — Packages SSIS",
        table_or_package="etl_run_log",
        cause="Un ou plusieurs packages ne sont pas au statut SUCCESS.",
        fix_steps=[
            "Vérifier les derniers runs avec la requête ci-dessous.",
            "Ouvrir le package en échec dans Visual Studio et lire l'onglet Progress.",
            "Consulter `etl_error_log` pour le message d'erreur détaillé.",
            "Corriger, réinitialiser le staging concerné, puis réexécuter le package.",
        ],
        diagnostic_sql="""
SELECT run_id, package_name, status, row_count_in, row_count_out, start_ts, end_ts
FROM etl_run_log
WHERE package_name IN ('PKG_DIM_CUSTOMER', 'PKG_DIM_PRODUCT', 'PKG_FACT_SALES')
ORDER BY run_id DESC;
""",
        reset_script=None,
    ),
}


DEMO_QC_ROWS = [
    ("QC-SS-01", "Volume raw_superstore", "9994", "> 9000", "PASS"),
    ("QC-SS-02", "Clients distincts stg_dim_customer", "793", "> 700", "PASS"),
    ("QC-SS-03", "Produits distincts stg_dim_product", "1862", "> 1800", "PASS"),
    ("QC-SS-04", "customer_id NULL dans stg_dim_customer", "0", "= 0", "PASS"),
    ("QC-SS-05", "product_id NULL dans stg_dim_product", "0", "= 0", "PASS"),
    ("QC-SS-06", "Lignes de fait sans dimension (lookup)", "3", "= 0", "FAIL"),
    ("QC-SS-07", "Ventes négatives dans stg_fact_sales", "0", "= 0", "PASS"),
    ("QC-SS-08", "Discount hors [0, 1] dans stg_fact_sales", "0", "= 0", "PASS"),
    ("QC-SS-09", "Doublons customer_id dans stg_dim_customer", "0", "= 0", "PASS"),
    ("QC-SS-10", "Doublons product_id dans stg_dim_product", "0", "= 0", "PASS"),
    ("QC-SS-11", "Réconciliation volume fait vs raw", "9991 / 9994", "= raw (lookup OK)", "WARN"),
    ("QC-SS-12", "Packages SSIS en SUCCESS", "2 / 3", "= 3", "FAIL"),
]

DEMO_DIAGNOSTICS: dict[str, pd.DataFrame] = {
    "QC-SS-06": pd.DataFrame(
        [
            {"row_id": 1042, "order_id": "US-2015-124151", "customer_id": "CG-12520", "product_id": "FUR-BO-10001798", "dim_customer": "OK", "dim_product": "MANQUANT"},
            {"row_id": 2107, "order_id": "US-2016-118962", "customer_id": "SC-20020", "product_id": "OFF-AR-10002726", "dim_customer": "MANQUANT", "dim_product": "OK"},
            {"row_id": 3891, "order_id": "US-2017-156720", "customer_id": "XK-99999", "product_id": "TEC-PH-10002275", "dim_customer": "MANQUANT", "dim_product": "MANQUANT"},
        ]
    ),
    "QC-SS-11": pd.DataFrame(
        [
            {"source": "raw_superstore", "nb": 9994},
            {"source": "stg_fact_sales", "nb": 9991},
            {"source": "rejets PKG_FACT_SALES", "nb": 3},
        ]
    ),
    "QC-SS-12": pd.DataFrame(
        [
            {"run_id": 12, "package_name": "PKG_FACT_SALES", "status": "STARTED", "row_count_in": None, "row_count_out": None},
            {"run_id": 11, "package_name": "PKG_DIM_PRODUCT", "status": "SUCCESS", "row_count_in": 1862, "row_count_out": 1862},
            {"run_id": 10, "package_name": "PKG_DIM_CUSTOMER", "status": "SUCCESS", "row_count_in": 793, "row_count_out": 793},
        ]
    ),
}


def _conn_str(server: str, database: str) -> str:
    return (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};DATABASE={database};Trusted_Connection=yes;TrustServerCertificate=yes;"
    )


def _frame(cursor) -> pd.DataFrame:
    if not cursor.description:
        return pd.DataFrame()
    return pd.DataFrame.from_records(cursor.fetchall(), columns=[c[0] for c in cursor.description])


def run_superstore_qc(server: str, database: str) -> tuple[pd.DataFrame, pd.DataFrame, str | None]:
    if pyodbc is None:
        return pd.DataFrame(), pd.DataFrame(), _NO_PYODBC_MSG
    try:
        with pyodbc.connect(_conn_str(server, database), timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute(QC_BATCH_SQL)
            qc_df = _frame(cursor)
            summary_df = pd.DataFrame()
            if cursor.nextset():
                summary_df = _frame(cursor)
            return qc_df, summary_df, None
    except Exception as exc:
        return pd.DataFrame(), pd.DataFrame(), str(exc)


def run_demo_qc() -> tuple[pd.DataFrame, pd.DataFrame]:
    qc_df = pd.DataFrame(
        DEMO_QC_ROWS,
        columns=["check_id", "check_name", "observed_value", "threshold", "status"],
    )
    summary_df = pd.DataFrame(
        [{"total_checks": 12, "passed": 9, "failed": 2, "warnings": 1}]
    )
    return qc_df, summary_df


def run_diagnostic(server: str, database: str, check_id: str) -> tuple[pd.DataFrame, str | None]:
    guide = QC_GUIDES.get(check_id)
    if not guide:
        return pd.DataFrame(), "Contrôle inconnu."
    if pyodbc is None:
        return pd.DataFrame(), _NO_PYODBC_MSG
    try:
        with pyodbc.connect(_conn_str(server, database), timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute(guide.diagnostic_sql)
            return _frame(cursor), None
    except Exception as exc:
        return pd.DataFrame(), str(exc)


def get_demo_diagnostic(check_id: str) -> pd.DataFrame:
    return DEMO_DIAGNOSTICS.get(check_id, pd.DataFrame())


def get_guide(check_id: str) -> QcGuide | None:
    return QC_GUIDES.get(check_id)
