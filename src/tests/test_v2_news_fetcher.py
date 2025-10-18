import pytest
from unittest.mock import patch, MagicMock
from v2_llm_graph.src.tools.news_fetcher import get_company_news

@pytest.fixture
def mock_newsapi_response():
    return {
        'status': 'ok',
        'articles': [
            {
                'source': {'name': 'Test Source 1'},
                'title': 'Test Title 1',
                'url': 'http://test1.com',
                'publishedAt': '2025-10-18T10:00:00Z',
                'content': 'Test content 1'
            },
            {
                'source': {'name': 'Test Source 2'},
                'title': 'Test Title 2',
                'url': 'http://test2.com',
                'publishedAt': '2025-10-18T11:00:00Z',
                'content': 'Test content 2'
            }
        ]
    }

def test_get_company_news_success(mock_newsapi_response):
    """Test successful news fetching and processing"""
    with patch('v2_llm_graph.src.tools.news_fetcher.NewsApiClient') as mock_client:
        # Arrange
        mock_instance = MagicMock()
        mock_instance.get_everything.return_value = mock_newsapi_response
        mock_client.return_value = mock_instance

        # Act
        result = get_company_news("Test Company", "fake_api_key", num_articles=2)

        # Assert
        assert "articles" in result
        assert len(result["articles"]) == 2
        assert result["articles"][0]["title"] == "Test Title 1"
        assert result["articles"][1]["content"] == "Test content 2"

def test_get_company_news_api_error():
    """Test handling of API errors"""
    with patch('v2_llm_graph.src.tools.news_fetcher.NewsApiClient') as mock_client:
        # Arrange
        mock_instance = MagicMock()
        mock_instance.get_everything.side_effect = Exception("API Error")
        mock_client.return_value = mock_instance

        # Act
        result = get_company_news("Test Company", "fake_api_key")

        # Assert
        assert "error" in result
        assert "An error occurred while fetching news" in result["error"]
        assert "API Error" in result["error"]

def test_get_company_news_failed_status():
    """Test handling of non-ok API status"""
    with patch('v2_llm_graph.src.tools.news_fetcher.NewsApiClient') as mock_client:
        # Arrange
        mock_instance = MagicMock()
        mock_instance.get_everything.return_value = {'status': 'error', 'articles': []}
        mock_client.return_value = mock_instance

        # Act
        result = get_company_news("Test Company", "fake_api_key")

        # Assert
        assert "error" in result
        assert result["error"] == "Failed to fetch news from NewsAPI."

def test_get_company_news_missing_content():
    """Test handling of articles with missing content"""
    with patch('v2_llm_graph.src.tools.news_fetcher.NewsApiClient') as mock_client:
        # Arrange
        mock_response = {
            'status': 'ok',
            'articles': [
                {
                    'source': {'name': 'Test Source'},
                    'title': 'Test Title',
                    'url': 'http://test.com',
                    'publishedAt': '2025-10-18T10:00:00Z'
                    # content field is intentionally missing
                }
            ]
        }
        mock_instance = MagicMock()
        mock_instance.get_everything.return_value = mock_response
        mock_client.return_value = mock_instance

        # Act
        result = get_company_news("Test Company", "fake_api_key")

        # Assert
        assert "articles" in result
        assert len(result["articles"]) == 1
        assert result["articles"][0]["content"] == "No content available."

def test_get_company_news_custom_num_articles():
    """Test fetching custom number of articles"""
    with patch('v2_llm_graph.src.tools.news_fetcher.NewsApiClient') as mock_client:
        # Arrange
        mock_instance = MagicMock()
        mock_instance.get_everything.return_value = {
            'status': 'ok',
            'articles': [{'source': {'name': f'Source {i}'}, 
                         'title': f'Title {i}',
                         'url': f'http://test{i}.com',
                         'publishedAt': '2025-10-18T10:00:00Z',
                         'content': f'Content {i}'} for i in range(10)]
        }
        mock_client.return_value = mock_instance

        # Act
        result = get_company_news("Test Company", "fake_api_key", num_articles=7)

        # Assert
        assert "articles" in result
        mock_instance.get_everything.assert_called_with(
            q="Test Company",
            language='en',
            sort_by='relevancy',
            page_size=7
        )