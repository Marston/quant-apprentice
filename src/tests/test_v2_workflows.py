import pytest
from unittest.mock import patch, MagicMock
import json
from v2_llm_graph.src.workflows.news_analysis_chain import analyze_article_chain
from v2_llm_graph.src.workflows.specialist_router import route_and_execute_task

# News Analysis Chain Tests
@pytest.fixture
def mock_llm():
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "reasoning": "The company's new product launch is expected to significantly boost revenue.",
        "sentiment": "Positive",
        "key_takeaways": [
            "Product targets high-growth market",
            "Initial customer feedback positive",
            "Revenue impact expected next quarter"
        ],
        "summary": "Company launches innovative product with strong market potential. Early indicators suggest positive customer adoption and revenue growth."
    })
    mock.generate_content.return_value = mock_response
    return mock

def test_analyze_article_success(mock_llm):
    """
    Test successful analysis of a news article.
    """
    # Arrange
    test_article = "Company XYZ announces groundbreaking new product launch."
    
    # Act
    result = analyze_article_chain(test_article, mock_llm)
    
    # Assert
    assert "error" not in result
    assert "reasoning" in result
    assert "sentiment" in result
    assert "key_takeaways" in result
    assert "summary" in result
    assert isinstance(result["key_takeaways"], list)
    assert len(result["key_takeaways"]) == 3
    assert result["sentiment"] in ["Positive", "Negative", "Neutral"]

def test_analyze_article_invalid_json(mock_llm):
    """
    Test handling of invalid JSON response from the LLM.
    """
    # Arrange
    mock_llm.generate_content.return_value.text = "Invalid JSON response"
    test_article = "Test article content"
    
    # Act
    result = analyze_article_chain(test_article, mock_llm)
    
    # Assert
    assert "error" in result
    assert "Failed to decode JSON" in result["error"]
    assert "raw_response" in result

def test_analyze_article_llm_error(mock_llm):
    """
    Test handling of LLM API errors.
    """
    # Arrange
    mock_llm.generate_content.side_effect = Exception("API Error")
    test_article = "Test article content"
    
    # Act
    result = analyze_article_chain(test_article, mock_llm)
    
    # Assert
    assert "error" in result
    assert "An unexpected error occurred" in result["error"]

def test_analyze_article_prompt_structure(mock_llm):
    """
    Test that the prompt includes all required analysis components.
    """
    # Arrange
    test_article = "Test article content"
    
    # Act
    analyze_article_chain(test_article, mock_llm)
    
    # Assert
    prompt = mock_llm.generate_content.call_args[0][0]
    assert "Analysis Steps:" in prompt
    assert "Sentiment Rubric:" in prompt
    assert "Positive" in prompt
    assert "Negative" in prompt
    assert "Neutral" in prompt
    assert test_article in prompt

# Specialist Router Tests
@pytest.fixture
def mock_specialist_llm():
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Specialist analysis result"
    mock.generate_content.return_value = mock_response
    return mock

def test_route_financial_analysis(mock_specialist_llm):
    """
    Test routing to financial analyst.
    """
    # Arrange
    test_data = {
        "revenue": "1B",
        "profit_margin": "15%"
    }
    
    # Act
    result = route_and_execute_task('analyze_financials', test_data, mock_specialist_llm)
    
    # Assert
    assert result == "Specialist analysis result"
    prompt = mock_specialist_llm.generate_content.call_args[0][0]
    assert "Quantitative Financial Analyst" in prompt
    assert str(test_data) in prompt

def test_route_news_analysis(mock_specialist_llm):
    """
    Test routing to news analyst.
    """
    # Arrange
    test_data = {
        "sentiment": "Positive",
        "summary": "Test news"
    }
    
    # Act
    result = route_and_execute_task('analyze_news_impact', test_data, mock_specialist_llm)
    
    # Assert
    assert result == "Specialist analysis result"
    prompt = mock_specialist_llm.generate_content.call_args[0][0]
    assert "Investment News Analyst" in prompt
    assert str(test_data) in prompt

def test_route_market_analysis(mock_specialist_llm):
    """
    Test routing to market analyst.
    """
    # Arrange
    test_data = {
        "GDP_Growth": "2.5%",
        "InflationRate": "3.2%"
    }
    
    # Act
    result = route_and_execute_task('analyze_market_context', test_data, mock_specialist_llm)
    
    # Assert
    assert result == "Specialist analysis result"
    prompt = mock_specialist_llm.generate_content.call_args[0][0]
    assert "Macroeconomic Analyst" in prompt
    assert str(test_data) in prompt

def test_route_invalid_task(mock_specialist_llm):
    """
    Test handling of invalid task type.
    """
    # Act
    result = route_and_execute_task('invalid_task', {}, mock_specialist_llm)
    
    # Assert
    assert "Invalid task type" in result
    mock_specialist_llm.generate_content.assert_not_called()

def test_route_llm_error(mock_specialist_llm):
    """
    Test handling of LLM API errors.
    """
    # Arrange
    mock_specialist_llm.generate_content.side_effect = Exception("API Error")
    
    # Act
    result = route_and_execute_task('analyze_financials', {}, mock_specialist_llm)
    
    # Assert
    assert "An error occurred" in result
    assert "API Error" in result