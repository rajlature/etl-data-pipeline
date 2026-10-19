
import logging
from pathlib import Path

import pandas as pd

from src.extract import extract_sales_data

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "product",
    "category",
    "quantity",
    "unit_price",
]


def transform_sales_data(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validate sales data, calculate revenue, and separate
    accepted records from rejected records.
    """

    # 1. Validate required columns.
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Work on a copy so the original DataFrame remains unchanged.
    data = df.copy()

    # 2. Standardize text fields.
    for column in ["product", "category"]:
        data[column] = data[column].astype("string").str.strip()
        data[column] = data[column].replace("", pd.NA)

    # 3. Convert columns to appropriate data types.
    data["order_id"] = pd.to_numeric(
        data["order_id"], errors="coerce"
    )

    data["quantity"] = pd.to_numeric(
        data["quantity"], errors="coerce"
    )

    data["unit_price"] = pd.to_numeric(
        data["unit_price"], errors="coerce"
    )

    data["order_date"] = pd.to_datetime(
        data["order_date"], errors="coerce"
    )

    # 4. Collect validation errors for each row.
    reasons = [[] for _ in range(len(data))]

    def reject_where(mask: pd.Series, reason: str) -> None:
        """Add a rejection reason to every invalid row."""
        invalid_rows = mask.fillna(True).tolist()

        for position, invalid in enumerate(invalid_rows):
            if invalid:
                reasons[position].append(reason)

    # Order ID must be a positive whole number.
    reject_where(
        data["order_id"].isna()
        | (data["order_id"] <= 0)
        | (data["order_id"] % 1 != 0),
        "order_id must be a positive whole number",
    )

    # Order date must be present and valid.
    reject_where(
        data["order_date"].isna(),
        "order_date is missing or invalid",
    )

    # Product and category must not be empty.
    for column in ["product", "category"]:
        reject_where(
            data[column].isna(),
            f"{column} is missing",
        )

    # Quantity must be a positive whole number.
    reject_where(
        data["quantity"].isna()
        | (data["quantity"] <= 0)
        | (data["quantity"] % 1 != 0),
        "quantity must be a positive whole number",
    )

    # Unit price must be a valid, non-negative number.
    reject_where(
        data["unit_price"].isna()
        | (data["unit_price"] < 0),
        "unit_price must be a non-negative number",
    )

    # 5. Reject duplicate IDs among otherwise valid records.
    # Keep the first valid occurrence of each order ID.
    valid_so_far = pd.Series(
        [not row_reasons for row_reasons in reasons],
        index=data.index,
    )

    duplicate_ids = pd.Series(False, index=data.index)

    duplicate_ids.loc[valid_so_far] = (
        data.loc[valid_so_far, "order_id"]
        .duplicated(keep="first")
    )

    reject_where(
        duplicate_ids,
        "duplicate order_id",
    )

    # 6. Separate accepted and rejected records.
    rejected_mask = pd.Series(
        [bool(row_reasons) for row_reasons in reasons],
        index=data.index,
    )

    rejected = df.loc[rejected_mask].copy()

    rejected["rejection_reason"] = [
        "; ".join(reasons[position])
        for position, is_rejected in enumerate(
            rejected_mask.tolist()
        )
        if is_rejected
    ]

    clean = data.loc[~rejected_mask].copy()

    # 7. Standardize accepted records.
    clean["order_id"] = clean["order_id"].astype("int64")
    clean["quantity"] = clean["quantity"].astype("int64")
    clean["unit_price"] = clean["unit_price"].round(2)

    # 8. Calculate revenue for each order.
    clean["revenue"] = (
        clean["quantity"] * clean["unit_price"]
    ).round(2)

    # Return columns in a consistent order.
    clean = clean[
        REQUIRED_COLUMNS + ["revenue"]
    ].reset_index(drop=True)

    rejected = rejected.reset_index(drop=True)

    logger.info(
        "Transformation completed: %d accepted, %d rejected",
        len(clean),
        len(rejected),
    )

    return clean, rejected


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    # Extract raw sales records.
    raw_df = extract_sales_data()

    # Transform and validate records.
    clean_df, rejected_df = transform_sales_data(raw_df)

    # Create output directories if they do not exist.
    processed_dir = PROJECT_ROOT / "data" / "processed"
    rejected_dir = PROJECT_ROOT / "data" / "rejected"

    processed_dir.mkdir(parents=True, exist_ok=True)
    rejected_dir.mkdir(parents=True, exist_ok=True)

    # Save accepted and rejected records separately.
    clean_path = processed_dir / "sales_clean.csv"
    rejected_path = rejected_dir / "sales_rejected.csv"

    clean_df.to_csv(clean_path, index=False)
    rejected_df.to_csv(rejected_path, index=False)

    print("\nClean data:")
    print(clean_df.to_string(index=False))

    print(f"\nAccepted records: {len(clean_df)}")
    print(f"Rejected records: {len(rejected_df)}")
    print(f"Clean data saved to: {clean_path}")
    print(f"Rejected data saved to: {rejected_path}")
