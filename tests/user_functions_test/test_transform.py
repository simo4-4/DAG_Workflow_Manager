from src.user_functions.offer_workflow_functions import transform_task
import polars as pl
import pytest

def test_transform_task():
    """Test if transform_task correctly transforms the data"""
    mock_df = pl.DataFrame({
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
    
    transformed_df, processed_count, failure_count = transform_task(mock_df)
    
    assert len(transformed_df) == 2 
    assert 'AVG_POINTS_BOUGHT' in transformed_df.columns
    assert 'PCT_GIFT_TRANSACTIONS' in transformed_df.columns
    
    member_1 = transformed_df.filter(pl.col('memberId') == 1)
    assert member_1.select('AVG_POINTS_BOUGHT').item() == pytest.approx(200.0) 
    assert member_1.select('PCT_GIFT_TRANSACTIONS').item() == pytest.approx(1/3)
    assert member_1.select('PCT_REDEEM_TRANSACTIONS').item() == pytest.approx(1/3)
    assert member_1.select('PCT_BUY_TRANSACTIONS').item() == pytest.approx(1/3)

def test_transform_task_handles_nulls():
    """Test if transform_task correctly handles null values"""
    mock_df = pl.DataFrame({
        'memberId': [1, 1, None, 2, 2],
        'lastTransactionUtcTs': [
            '2024-01-01 10:00:00',
            '2024-01-02 11:00:00',
            '2024-01-03 12:00:00',
            None,
            '2024-01-02 14:00:00'
        ],
        'lastTransactionPointsBought': [100, None, 300, 150, 250],
        'lastTransactionRevenueUSD': [10, 20, 30, 15, None],
        'lastTransactionType': ['buy', 'gift', None, 'buy', 'gift']
    })
    
    transformed_df, processed_count, failure_count = transform_task(mock_df)
    
    assert len(transformed_df) == 1

def test_transform_task_last_3_transactions():
    """Test if transform_task correctly calculates last 3 transactions metrics"""
    mock_df = pl.DataFrame({
        'memberId': [1, 1, 1, 1, 1],
        'lastTransactionUtcTs': [
            '2024-01-01 10:00:00',
            '2024-01-02 11:00:00',
            '2024-01-03 12:00:00',
            '2024-01-04 13:00:00',
            '2024-01-05 14:00:00'
        ],
        'lastTransactionPointsBought': [100, 200, 300, 400, 500],
        'lastTransactionRevenueUSD': [10, 20, 30, 40, 50],
        'lastTransactionType': ['buy', 'gift', 'redeem', 'buy', 'gift']
    })
    
    transformed_df, processed_count, failure_count = transform_task(mock_df)
    
    last_3_points = transformed_df.select('LAST_3_TRANSACTIONS_AVG_POINTS_BOUGHT').item()
    assert last_3_points == pytest.approx(400.0)  # (300 + 400 + 500) / 3