import pytest
from unittest.mock import patch, MagicMock
import google.generativeai as genai
from v2_llm_graph.src.agent_graph import (
    AgentState,
    gather_data_node,
    specialist_analysis_node,
    synthesize_report_node,
    evaluate_report_node,
    refine_report_node,
    retrieve_from_memory_node,
    save_to_memory_node,
    should_refine_or_end,
    workflow,
    app
)

@pytest.fixture
def mock_state():
    """
    Create a mock agent state with test data.
    """
    return AgentState(
        company_name="Test Company",
        company_ticker="TEST",
        financial_data={},
        macro_data={},
        news_data={"articles": []},
        structured_news_analysis={},
        financial_analysis="",
        news_impact_analysis="",
        market_context_analysis="",
        draft_report="",
        sec_filings_data={},
        past_analysis="",
        feedback="",
        final_report="",
        revision_count=0
    )

@pytest.fixture
def mock_llm():
    mock = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Mock LLM Response"
    mock.generate_content.return_value = mock_response
    return mock

@patch('v2_llm_graph.src.agent_graph.get_stock_fundamentals')
@patch('v2_llm_graph.src.agent_graph.get_macro_economic_data')
@patch('v2_llm_graph.src.agent_graph.get_company_news')
def test_gather_data_node(mock_news, mock_macro, mock_stock, mock_state):
    """
    Test the gather_data_node functionality.
    """
    # Arrange
    mock_stock.return_value = {"stock": "data"}
    mock_macro.return_value = {"macro": "data"}
    mock_news.return_value = {"articles": []}
    
    # Act
    result = gather_data_node(mock_state)
    
    # Assert
    assert "financial_data" in result
    assert "macro_data" in result
    assert "news_data" in result
    mock_stock.assert_called_once_with("TEST")
    mock_news.assert_called_once()
    mock_macro.assert_called_once()

@patch('v2_llm_graph.src.agent_graph.VectorMemory')
def test_retrieve_from_memory_node(mock_vector_memory, mock_state):
    """
    Test memory retrieval functionality.
    """
    # Arrange
    mock_instance = mock_vector_memory.return_value
    mock_instance.query_memory.return_value = ["Past analysis result"]
    
    # Act
    result = retrieve_from_memory_node(mock_state)
    
    # Assert
    assert "past_analysis" in result
    assert "Past analysis result" in result["past_analysis"]
    mock_instance.query_memory.assert_called_once()

@patch('v2_llm_graph.src.agent_graph.analyze_article_chain')
@patch('v2_llm_graph.src.agent_graph.route_and_execute_task')
def test_specialist_analysis_node(mock_route, mock_analyze, mock_state, mock_llm):
    """
    Test the specialist analysis functionality.
    """
    # Arrange
    mock_state['news_data'] = {"articles": [{"content": "test news"}]}
    mock_analyze.return_value = {"sentiment": "positive"}
    mock_route.return_value = "Analysis result"
    
    # Act
    result = specialist_analysis_node(mock_state)
    
    # Assert
    assert "structured_news_analysis" in result
    assert "financial_analysis" in result
    assert "news_impact_analysis" in result
    assert "market_context_analysis" in result
    mock_analyze.assert_called_once()
    assert mock_route.call_count == 3

def test_should_refine_or_end_max_revisions(mock_state):
    """
    Test that the refinement process ends after max revisions.
    """
    # Arrange
    mock_state['revision_count'] = 2
    mock_state['feedback'] = "Some feedback"
    
    # Act
    result = should_refine_or_end(mock_state)
    
    # Assert
    assert result == "end"

@patch('v2_llm_graph.src.agent_graph.llm')
def test_should_refine_or_end_needs_revision(mock_llm, mock_state):
    """
    Test refinement decision when feedback suggests changes needed.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.text = "Yes"
    mock_llm.generate_content.return_value = mock_response
    mock_state['feedback'] = "This report needs improvement"
    mock_state['revision_count'] = 1
    
    # Act
    result = should_refine_or_end(mock_state)
    
    # Assert
    assert result == "refine"

@patch('v2_llm_graph.src.agent_graph.VectorMemory')
def test_save_to_memory_node(mock_vector_memory, mock_state):
    """
    Test saving the final report to memory.
    """
    # Arrange
    mock_state['final_report'] = "Final analysis report"
    mock_instance = mock_vector_memory.return_value
    
    # Act
    result = save_to_memory_node(mock_state)
    
    # Assert
    mock_instance.add_analysis.assert_called_once_with("TEST", "Final analysis report")
    assert result == {}

def test_workflow_structure():
    """
    Test that the workflow graph is properly structured.
    """
    # Assert nodes are present
    assert "gather_data" in workflow.nodes
    assert "retrieve_from_memory" in workflow.nodes
    assert "analyze_specialists" in workflow.nodes
    assert "synthesize_report" in workflow.nodes
    assert "evaluate_report" in workflow.nodes
    assert "refine_report" in workflow.nodes
    assert "save_to_memory" in workflow.nodes

@patch('v2_llm_graph.src.agent_graph.llm')
def test_synthesize_report_node(mock_llm, mock_state):
    """
    Test report synthesis functionality.
    """
    # Arrange
    mock_response = MagicMock()
    mock_response.text = "Synthesized report"
    mock_llm.generate_content.return_value = mock_response
    
    # Act
    result = synthesize_report_node(mock_state)
    
    # Assert
    assert "draft_report" in result
    assert result["draft_report"] == "Synthesized report"
    assert "revision_count" in result
    assert result["revision_count"] == 1