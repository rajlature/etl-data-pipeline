from src.logging_config import setup_logging
import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "product",
    "category",
    "quantity",
    "unit_price",
    "revenue",
]


def get_engine() -> Engine:
    """Create a MySQL engine using settings from .env."""

    required_settings = [
        "MYSQL_HOST",
        "MYSQL_PORT",
        "MYSQL_DATABASE",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
    ]

    missing = [
        key for key in required_settings if not os.getenv(key)
    ]

    if missing:
        raise ValueError(f"Missing MySQL settings in .env: {missing}")

    connection_url = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        database=os.getenv("MYSQL_DATABASE"),
    )

    return create_engine(connection_url, pool_pre_ping=True)


def create_sales_table(engine: Engine) -> None:
    """Create the sales table if it does not exist."""

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS sales (
        order_id BIGINT PRIMARY KEY,
        order_date DATE NOT NULL,
        product VARCHAR(150) NOT NULL,
        category VARCHAR(100) NOT NULL,
        quantity INT NOT NULL,
        unit_price DECIMAL(12, 2) NOT NULL,
        revenue DECIMAL(14, 2) NOT NULL
    )
    """

    with engine.begin() as connection:
        connection.execute(text(create_table_sql))

    logger.info("Sales table is ready")


def load_sales_data(
    df: pd.DataFrame,
    engine: Engine | None = None,
) -> int:
    """Insert new sales records or update existing order IDs."""

    if df.empty:
        logger.warning("No sales records to load")
        return 0

    missing = [
        col for col in REQUIRED_COLUMNS if col not in df.columns
    ]
    if missing:
        raise ValueError(f"Missing columns required for loading: {missing}")

    # A DataFrame must not contain duplicate order IDs before loading.
    if df["order_id"].duplicated().any():
        raise ValueError("Input data contains duplicate order_id values")

    own_engine = engine is None
    if own_engine:
        engine = get_engine()

    try:
        create_sales_table(engine)

        # Explicit SQL enables MySQL's duplicate-key update behavior.
        upsert_sql = text("""
            INSERT INTO sales (
                order_id, order_date, product, category,
                quantity, unit_price, revenue
            )
            VALUES (
                :order_id, :order_date, :product, :category,
                :quantity, :unit_price, :revenue
            )
            ON DUPLICATE KEY UPDATE
                order_date = VALUES(order_date),
                product = VALUES(product),
                category = VALUES(category),
                quantity = VALUES(quantity),
                unit_price = VALUES(unit_price),
                revenue = VALUES(revenue)
        """)

        records = df[REQUIRED_COLUMNS].copy()
        records["order_date"] = pd.to_datetime(
            records["order_date"], errors="raise"
        ).dt.date

        # Convert pandas/numpy values to ordinary Python values.
        rows = records.to_dict(orient="records")
        with engine.begin() as connection:
            connection.execute(upsert_sql, rows)

        logger.info("Loaded or updated %d sales records", len(rows))
        return len(rows)

    finally:
        if own_engine:
            engine.dispose()


if __name__ == "__main__":
    setup_logging()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    clean_path = PROJECT_ROOT / "data" / "processed" / "sales_clean.csv"

    if not clean_path.exists():
        raise FileNotFoundError(
            f"Clean data not found: {clean_path}. "
            "Run 'python -m src.transform' first."
        )

    clean_df = pd.read_csv(clean_path, parse_dates=["order_date"])
    count = load_sales_data(clean_df)
    print(f"Records loaded or updated in MySQL: {count}")
