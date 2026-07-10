"""
Ingest Superstore CSV into SQL Server landing table raw_superstore.

Usage:
    pip install pandas pyodbc
    python samples/python/ingest_superstore_to_sql.py
    python samples/python/ingest_superstore_to_sql.py --csv "samples/data/superstore/Sample - Superstore.csv"
    python samples/python/ingest_superstore_to_sql.py --download
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import pyodbc

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT / "samples" / "data" / "superstore"
DEFAULT_CSV_NAMES = [
    "Sample - Superstore.csv",
    "superstore.csv",
    "Sample-Superstore.csv",
]

# Mirror public pour demo / tests si le fichier Kaggle n'est pas encore telecharge
DEFAULT_DOWNLOAD_URL = (
    "https://raw.githubusercontent.com/Oyiwoche/Superstore-Analytics/"
    "main/Sample%20-%20Superstore.csv"
)

CSV_TO_SQL = {
    "Row ID": "row_id",
    "Order ID": "order_id",
    "Order Date": "order_date",
    "Ship Date": "ship_date",
    "Ship Mode": "ship_mode",
    "Customer ID": "customer_id",
    "Customer Name": "customer_name",
    "Segment": "segment",
    "Country": "country",
    "City": "city",
    "State": "state",
    "Postal Code": "postal_code",
    "Region": "region",
    "Product ID": "product_id",
    "Category": "category",
    "Sub-Category": "sub_category",
    "Product Name": "product_name",
    "Sales": "sales",
    "Quantity": "quantity",
    "Discount": "discount",
    "Profit": "profit",
}

SQL_COLUMNS = [
    "row_id",
    "order_id",
    "order_date",
    "ship_date",
    "ship_mode",
    "customer_id",
    "customer_name",
    "segment",
    "country",
    "city",
    "state",
    "postal_code",
    "region",
    "product_id",
    "category",
    "sub_category",
    "product_name",
    "sales",
    "quantity",
    "discount",
    "profit",
    "source_file",
    "ingest_batch_id",
]


def find_csv_file(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            raise FileNotFoundError(f"Fichier CSV introuvable : {path}")
        return path

    for name in DEFAULT_CSV_NAMES:
        candidate = DEFAULT_DATA_DIR / name
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Aucun CSV Superstore trouve. Placez le fichier dans "
        f"{DEFAULT_DATA_DIR} ou utilisez --csv / --download.\n"
        "Voir samples/python/README_superstore.md"
    )


def download_csv(target: Path, url: str) -> Path:
    import urllib.request

    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"Telechargement : {url}")
    urllib.request.urlretrieve(url, target)
    print(f"Fichier enregistre : {target}")
    return target


def load_csv(path: Path) -> pd.DataFrame:
    last_error: Exception | None = None
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            df = pd.read_csv(path, encoding=encoding)
            break
        except UnicodeDecodeError as exc:
            last_error = exc
    else:
        raise last_error or RuntimeError("Impossible de lire le CSV")

    missing = [col for col in CSV_TO_SQL if col not in df.columns]
    if missing:
        raise ValueError(
            "Colonnes CSV manquantes : "
            + ", ".join(missing)
            + f"\nColonnes trouvees : {list(df.columns)}"
        )

    out = df.rename(columns=CSV_TO_SQL).copy()

    for date_col in ("order_date", "ship_date"):
        out[date_col] = pd.to_datetime(out[date_col], errors="coerce").dt.date

    for num_col in ("sales", "discount", "profit"):
        out[num_col] = pd.to_numeric(out[num_col], errors="coerce")

    out["quantity"] = pd.to_numeric(out["quantity"], errors="coerce").astype("Int64")
    out["row_id"] = pd.to_numeric(out["row_id"], errors="coerce").astype("Int64")

    out["source_file"] = path.name
    return out


def build_connection(server: str, database: str) -> pyodbc.Connection:
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    try:
        return pyodbc.connect(conn_str)
    except pyodbc.Error:
        conn_str = conn_str.replace("ODBC Driver 17", "ODBC Driver 18")
        return pyodbc.connect(conn_str)


def truncate_raw_table(cursor: pyodbc.Cursor) -> None:
    cursor.execute("TRUNCATE TABLE raw_superstore;")


def to_python_scalar(value: object) -> object:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def insert_dataframe(
    cursor: pyodbc.Cursor,
    df: pd.DataFrame,
    batch_id: int,
) -> int:
    df = df.copy()
    df["ingest_batch_id"] = batch_id

    placeholders = ", ".join("?" for _ in SQL_COLUMNS)
    columns_sql = ", ".join(SQL_COLUMNS)
    insert_sql = f"INSERT INTO raw_superstore ({columns_sql}) VALUES ({placeholders})"

    rows = []
    for record in df[SQL_COLUMNS].itertuples(index=False, name=None):
        rows.append(tuple(to_python_scalar(v) for v in record))

    cursor.fast_executemany = True
    cursor.executemany(insert_sql, rows)
    return len(rows)


def print_summary(cursor: pyodbc.Cursor) -> None:
    cursor.execute(
        """
        SELECT
            COUNT(*) AS raw_rows,
            COUNT(DISTINCT customer_id) AS customers,
            COUNT(DISTINCT product_id) AS products,
            MIN(order_date) AS min_order_date,
            MAX(order_date) AS max_order_date
        FROM raw_superstore;
        """
    )
    row = cursor.fetchone()
    print("\n--- Resume landing raw_superstore ---")
    print(f"Lignes          : {row.raw_rows}")
    print(f"Clients distincts : {row.customers}")
    print(f"Produits distincts: {row.products}")
    print(f"Periode commandes : {row.min_order_date} -> {row.max_order_date}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest Superstore CSV vers SQL Server")
    parser.add_argument("--csv", help="Chemin vers le fichier CSV")
    parser.add_argument(
        "--download",
        action="store_true",
        help="Telecharger Sample - Superstore.csv si absent",
    )
    parser.add_argument(
        "--download-url",
        default=DEFAULT_DOWNLOAD_URL,
        help="URL du CSV public (demo)",
    )
    parser.add_argument("--server", default=r"localhost\SQLEXPRESS")
    parser.add_argument("--database", default="POC_ETL_IA")
    parser.add_argument("--batch-id", type=int, default=1)
    parser.add_argument(
        "--no-truncate",
        action="store_true",
        help="Ne pas vider raw_superstore avant insert",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        if args.csv or not args.download:
            csv_path = find_csv_file(args.csv)
        else:
            csv_path = DEFAULT_DATA_DIR / "Sample - Superstore.csv"
            if not csv_path.exists():
                csv_path = download_csv(csv_path, args.download_url)
    except FileNotFoundError as exc:
        if args.download:
            csv_path = DEFAULT_DATA_DIR / "Sample - Superstore.csv"
            csv_path = download_csv(csv_path, args.download_url)
        else:
            print(exc, file=sys.stderr)
            print("\nAstuce : python ingest_superstore_to_sql.py --download", file=sys.stderr)
            return 1

    print(f"Lecture CSV : {csv_path}")
    df = load_csv(csv_path)
    print(f"Lignes lues : {len(df)}")

    conn = build_connection(args.server, args.database)
    try:
        cursor = conn.cursor()
        if not args.no_truncate:
            print("TRUNCATE raw_superstore...")
            truncate_raw_table(cursor)

        inserted = insert_dataframe(cursor, df, args.batch_id)
        conn.commit()
        print(f"Lignes inserees : {inserted}")
        print_summary(cursor)
    finally:
        conn.close()

    print("\nIngest termine. Prochaine etape : 7B-3 package SSIS PKG_DIM_CUSTOMER.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
