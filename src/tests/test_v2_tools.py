import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

from v2_llm_graph.src.tools.financial_data_fetcher import get_stock_fundamentals, get_macro_economic_data
from v2_llm_graph.src.tools.news_fetcher import get_company_news
from v2_llm_graph.src.tools.sec_filings_fetcher import get_latest_sec_filings

@patch('yfinance.Ticker')
def test_get_stock_fundamentals_success(MockTicker):
    """
    Tests the successful retrieval of stock fundamentals.
    """
    # Arrange
    mock_instance = MockTicker.return_value
    mock_instance.info = {
        'longName': 'Apple Inc.',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'marketCap': 2000000000000,
        'enterpriseValue': 2100000000000,
        'trailingPE': 30.5,
        'forwardPE': 25.2,
        'trailingEps': 6.5,
        'priceToBook': 35.2,
        'dividendYield': 0.65,
        'payoutRatio': 0.15
    }

    # Act
    result = get_stock_fundamentals("AAPL")

    # Assert
    assert result["companyName"] == "Apple Inc."
    assert result["marketCap"] == 2000000000000
    assert "error" not in result

@patch('yfinance.Ticker')
def test_get_stock_fundamentals_invalid_ticker(MockTicker):
    """
    Tests the function with an invalid ticker.
    """
    # Arrange
    mock_instance = MockTicker.return_value
    mock_instance.info = MagicMock()
    mock_instance.info.get.side_effect = Exception("Invalid ticker")

    # Act
    result = get_stock_fundamentals("INVALIDTICKER")

    # Assert
    assert "error" in result
    assert "Could not fetch data" in result["error"]

@patch('v2_llm_graph.src.tools.financial_data_fetcher.Fred')
def test_get_macro_economic_data_success(MockFred):
    """
    Tests the successful retrieval of macroeconomic data.
    """
    # Arrange
    mock_instance = MockFred.return_value
    mock_series = pd.Series([3.2])
    # Mock each series request to return our mock data
    mock_instance.get_series_latest_release = MagicMock()
    mock_instance.get_series_latest_release.return_value = mock_series

    # Act
    result = get_macro_economic_data("fake_api_key")

    # Assert
    assert len(result) > 0
    assert "error" not in result

@patch('fredapi.Fred')
def test_get_macro_economic_data_error(MockFred):
    """
    Tests error handling in macroeconomic data retrieval.
    """
    # Arrange
    mock_instance = MockFred.return_value
    mock_instance.get_series_latest_release.side_effect = Exception("API Error")

    # Act
    result = get_macro_economic_data("invalid_api_key")

    # Assert
    assert "error" in result
    assert "Could not fetch FRED data" in result["error"]

# Keep existing news and SEC filing tests