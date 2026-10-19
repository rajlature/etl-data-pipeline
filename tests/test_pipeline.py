
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from src.extract import extract_sales_data
from src.transform import transform_sales_data
from src.load import load_sales_data


def test_pipeline_end_to_end(tmp_path: Path):
    # 1. Create a temporary input CSV.
    raw_file = tmp_path / "sales.csv"

    input_df = pd.DataFrame(
        [
            {
                "order_id": 9001,
                "order_date": "2026-10-10",
                "product": "Laptop",
                "category": "Electronics",
                "quantity": 2,
                "unit_price": 1000,
            },
            {
                "order_id": 9002,
                "order_date": "2026-10-11",
                "product": "Mouse",
                "category": "Accessories",
                "quantity": 3,
                "unit_price": 200,
            },
        ]
    )
    input_df.to_csv(raw_file, index=False)

    # 2. Extract the input data.
    extracted_df = extract_sales_data(raw_file)
    assert len(extracted_df) == 2

    # 3. Transform and validate the data.
    clean_df, rejected_df = transform_sales_data(extracted_df)

    assert len(clean_df) == 2
    assert rejected_df.empty
    assert clean_df["revenue"].tolist() == [2000, 600]

    # 4. Load into a temporary SQLite database.
    engine = create_engine("sqlite:///:memory:")

    try:
        loaded_count = load_sales_data(clean_df, engine=engine)

        assert loaded_count == 2

        # 5. Verify the records actually reached the database.
        with engine.connect() as connection:
            result = connection.execute(
                text(
                    "SELECT COUNT(*), SUM(revenue) "
                    "FROM sales"
                )
            ).one()

        assert result[0] == 2
        assert float(result[1]) == 2600.0

    finally:
        engine.dispose()
