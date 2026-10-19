
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Locate the project root independently of the terminal's directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV_PATH = PROJECT_ROOT / "data" / "raw" / "sales.csv"


def extract_sales_data(
    file_path: str | Path = DEFAULT_CSV_PATH,
) -> pd.DataFrame:
    """Read raw sales records from a CSV file."""
    csv_path = Path(file_path)

    logger.info("Starting extraction from %s", csv_path)

    if not csv_path.is_file():
        raise FileNotFoundError(
            f"Sales CSV file not found: {csv_path}"
        )

    df = pd.read_csv(csv_path)

    if df.empty:
        raise ValueError("The sales CSV file contains no records.")

    logger.info("Extracted %d rows and %d columns", *df.shape)

    return df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    sales_df = extract_sales_data()

    print("\nFirst five records:")
    print(sales_df.head())

    print("\nDataset information:")
    print(f"Rows: {len(sales_df)}")
    print(f"Columns: {list(sales_df.columns)}")
