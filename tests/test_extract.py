import pytest
import polars as pl
from src.offer_workflow_functions import extract_task

@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file for testing."""
    df = pl.DataFrame({
        'memberId': [1, 1, 1, 2, 2],
        'lastTransactionUtcTs': [
            '2024-01-01 10:00:00',
            '2024-01-02 11:00:00',
            '2024-01-03 12:00:00',
            '2024-01-01 13:00:00',
            '2024-01-02 14:00:00'
        ],
        'lastTransactionPointsBought': [100, 200, 300, 150, 250],
        'lastTransactionRevenueUSD': [10, 20, 30, 15, 25],
        'lastTransactionType': ['buy', 'gift', 'redeem', 'buy', 'gift']
    })
    
    csv_path = tmp_path / "test_data.csv"
    df.write_csv(csv_path)
    return str(csv_path)

def test_extract_task(sample_csv):
    """Test if extract_task correctly loads CSV data."""
    df, count = extract_task(sample_csv)
    
    assert isinstance(df, pl.DataFrame)
    assert count == 5
    assert list(df.columns) == [
        'memberId', 
        'lastTransactionUtcTs', 
        'lastTransactionPointsBought',
        'lastTransactionRevenueUSD', 
        'lastTransactionType'
    ]