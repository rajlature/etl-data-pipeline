
import pandas as pd
import pytest

from src.transform import transform_sales_data


@pytest.fixture
def sample_sales():
    """Create sample sales data for testing."""
    return pd.DataFrame(
        {
            "order_id": [1001, 1002, 1003],
            "order_date": [
                "2026-10-01",
                "2026-10-02",
                "2026-10-03",
            ],
            "product": ["Laptop", "Mouse", "Keyboard"],
            "category": [
                "Electronics",
                "Accessories",
                "Accessories",
            ],
            "quantity": [2, 5, 3],
            "unit_price": [55000, 500, 1200],
        }
    )


def test_valid_records_are_accepted(sample_sales):
    clean, rejected = transform_sales_data(sample_sales)

    assert len(clean) == 3
    assert len(rejected) == 0


def test_revenue_is_calculated_correctly(sample_sales):
    clean, _ = transform_sales_data(sample_sales)

    assert clean.loc[0, "revenue"] == 110000
    assert clean.loc[1, "revenue"] == 2500
    assert clean.loc[2, "revenue"] == 3600


def test_invalid_quantity_is_rejected(sample_sales):
    sample_sales.loc[0, "quantity"] = -2

    clean, rejected = transform_sales_data(sample_sales)

    assert len(clean) == 2
    assert len(rejected) == 1
    assert "quantity must be a positive whole number" in (
        rejected.loc[0, "rejection_reason"]
    )


def test_duplicate_order_id_is_rejected(sample_sales):
    sample_sales.loc[1, "order_id"] = 1001

    clean, rejected = transform_sales_data(sample_sales)

    assert len(clean) == 2
    assert len(rejected) == 1
    assert "duplicate order_id" in (
        rejected.loc[0, "rejection_reason"]
    )


def test_missing_product_is_rejected(sample_sales):
    sample_sales.loc[0, "product"] = ""

    clean, rejected = transform_sales_data(sample_sales)

    assert len(clean) == 2
    assert len(rejected) == 1
    assert "product is missing" in (
        rejected.loc[0, "rejection_reason"]
    )


def test_missing_required_column_raises_error(sample_sales):
    sample_sales = sample_sales.drop(columns=["product"])

    with pytest.raises(ValueError, match="Missing required columns"):
        transform_sales_data(sample_sales)
