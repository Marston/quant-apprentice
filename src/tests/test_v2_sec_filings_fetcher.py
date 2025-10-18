import pytest
from unittest.mock import patch, MagicMock
from v2_llm_graph.src.tools.sec_filings_fetcher import get_latest_sec_filings

@pytest.fixture
def mock_sec_response():
    return {
        'filings': [{
            'formType': '10-K',
            'filedAt': '2025-10-18T10:00:00Z',
            'linkToFilingDetails': 'https://sec.gov/test/filing.html'
        }]
    }

def test_get_latest_sec_filings_success(mock_sec_response):
    """Test successful SEC filing retrieval"""
    with patch('v2_llm_graph.src.tools.sec_filings_fetcher.QueryApi') as mock_api:
        # Arrange
        mock_instance = MagicMock()
        mock_instance.get_filings.return_value = mock_sec_response
        mock_api.return_value = mock_instance

        # Act
        result = get_latest_sec_filings('AAPL', 'fake_api_key')

        # Assert
        assert result['filing_type'] == '10-K'
        assert result['filed_at'] == '2025-10-18T10:00:00Z'
        assert result['link_to_filing'] == 'https://sec.gov/test/filing.html'
        assert 'summary_of_risk_factors' in result
        assert 'summary_of_mdna' in result

def test_get_latest_sec_filings_no_results():
    """Test handling of no filing results"""
    with patch('v2_llm_graph.src.tools.sec_filings_fetcher.QueryApi') as mock_api:
        # Arrange
        mock_instance = MagicMock()
        mock_instance.get_filings.return_value = {'filings': []}
        mock_api.return_value = mock_instance

        # Act
        result = get_latest_sec_filings('INVALID', 'fake_api_key')

        # Assert
        assert 'error' in result
        assert 'No recent 10-K or 10-Q found' in result['error']

def test_get_latest_sec_filings_api_error():
    """Test handling of API errors"""
    with patch('v2_llm_graph.src.tools.sec_filings_fetcher.QueryApi') as mock_api:
        # Arrange
        mock_instance = MagicMock()
        mock_instance.get_filings.side_effect = Exception("API Error")
        mock_api.return_value = mock_instance

        # Act
        result = get_latest_sec_filings('AAPL', 'fake_api_key')

        # Assert
        assert 'error' in result
        assert 'API Error' in result['error']

def test_get_latest_sec_filings_query_structure():
    """Test the structure of the SEC API query"""
    with patch('v2_llm_graph.src.tools.sec_filings_fetcher.QueryApi') as mock_api:
        # Arrange
        mock_instance = MagicMock()
        mock_instance.get_filings.return_value = {'filings': []}
        mock_api.return_value = mock_instance

        # Act
        get_latest_sec_filings('AAPL', 'fake_api_key')

        # Assert
        query = mock_instance.get_filings.call_args[0][0]
        assert 'query' in query
        assert 'ticker:AAPL' in query['query']['query_string']['query']
        assert 'formType:"10-K" OR formType:"10-Q"' in query['query']['query_string']['query']
        assert query['size'] == '1'
        assert query['sort'][0]['filedAt']['order'] == 'desc'