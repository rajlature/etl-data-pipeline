
import pandas as pd
import pytest
from sqlalchemy import create_engine, text

from src.load import load_sales_data


@pytest.fixture
def engine():
    """Create a temporary database for testing."""
    test_engine = create_engine("sqlite:///:memory:")
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def sample_sales():
    """Create sample sales records."""
    return pd.DataFrame([
        {
            "order_id": 1001,
            "order_date": "2026-10-01",
            "product": "Laptop",
            "category": "Electronics",
            "quantity": 2,
            "unit_price": 55000,
            "revenue": 110000,
        },
        {
            "order_id": 1002,
            "order_date": "2026-10-02",
            "product": "Mouse",
            "category": "Accessories",
            "quantity": 5,
            "unit_price": 500,
            "revenue": 2500,
        },
    ])


def test_load_inserts_records(engine, sample_sales):
    count = load_sales_data(sample_sales, engine)

    assert count == 2

    with engine.connect() as connection:
        total = connection.execute(
            text("SELECT COUNT(*) FROM sales")
        ).scalar_one()

    assert total == 2


def test_load_updates_existing_order(engine, sample_sales):
    load_sales_data(sample_sales, engine)

    updated = sample_sales.iloc[[0]].copy()
    updated.loc[:, "quantity"] = 3
    updated.loc[:, "revenue"] = 165000

    count = load_sales_data(updated, engine)

    assert count == 1

    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT quantity, revenue "
                "FROM sales WHERE order_id = 1001"
            )
        ).one()

    assert result.quantity == 3
    assert float(result.revenue) == 165000


def test_empty_dataframe_loads_zero_rows(engine):
    assert load_sales_data(pd.DataFrame(), engine) == 0


def test_missing_column_raises_error(engine, sample_sales):
    incomplete = sample_sales.drop(columns=["revenue"])

    with pytest.raises(ValueError, match="Missing columns"):
        load_sales_data(incomplete, engine)


def test_duplicate_ids_in_input_are_rejected(engine, sample_sales):
    duplicated = pd.concat(
        [sample_sales, sample_sales.iloc[[0]]],
        ignore_index=True,
    )

    with pytest.raises(ValueError, match="duplicate order_id"):
        load_sales_data(duplicated, engine)
