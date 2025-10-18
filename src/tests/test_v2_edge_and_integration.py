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

# Edge Cases
def test_gather_data_node_api_failure(mock_state):
    """
    Test gather_data_node handling of API failures.
    """
    with patch('v2_llm_graph.src.agent_graph.get_stock_fundamentals') as mock_stock:
        with patch('v2_llm_graph.src.agent_graph.get_macro_economic_data') as mock_macro:
            with patch('v2_llm_graph.src.agent_graph.get_company_news') as mock_news:
                # Arrange
                mock_stock.side_effect = Exception("API Error")
                mock_macro.return_value = {"macro": "data"}
                mock_news.return_value = {"articles": []}
                
                # Act
                result = gather_data_node(mock_state)
                
                # Assert
                assert "financial_data" in result
                assert "error" in result["financial_data"]
                assert "macro_data" in result
                assert "news_data" in result

def test_specialist_analysis_empty_data(mock_state):
    """
    Test specialist analysis handling of empty input data.
    """
    # Arrange
    mock_state['news_data'] = {"articles": []}
    mock_state['financial_data'] = {}
    mock_state['macro_data'] = {}
    
    with patch('v2_llm_graph.src.agent_graph.route_and_execute_task') as mock_route:
        mock_route.return_value = "Empty data analysis"
        
        # Act
        result = specialist_analysis_node(mock_state)
        
        # Assert
        assert "structured_news_analysis" in result
        assert "news_items" in result["structured_news_analysis"]
        assert len(result["structured_news_analysis"]["news_items"]) == 0

def test_memory_database_connection_error(mock_state):
    """
    Test memory operations when database connection fails.
    """
    with patch('v2_llm_graph.src.agent_graph.VectorMemory') as mock_memory:
        # Arrange
        mock_memory.side_effect = Exception("Database connection failed")
        
        # Act
        result = retrieve_from_memory_node(mock_state)
        
        # Assert
        assert "past_analysis" in result
        assert "Error accessing memory system" in result["past_analysis"]
        assert "Database connection failed" in result["past_analysis"]

def test_llm_timeout_handling(mock_state):
    """
    Test handling of LLM API timeouts.
    """
    with patch('v2_llm_graph.src.agent_graph.llm.generate_content') as mock_generate:
        # Arrange
        mock_generate.side_effect = Exception("API timeout")
        
        # Act
        result = synthesize_report_node(mock_state)
        
        # Assert
        assert "draft_report" in result
        assert "error" in result["draft_report"].lower()
        assert result["revision_count"] == 1

# Integration Tests
@pytest.mark.integration
def test_full_workflow_success():
    """
    Test successful end-to-end workflow execution.
    """
    with patch('v2_llm_graph.src.agent_graph.get_stock_fundamentals') as mock_stock, \
         patch('v2_llm_graph.src.agent_graph.get_macro_economic_data') as mock_macro, \
         patch('v2_llm_graph.src.agent_graph.get_company_news') as mock_news, \
         patch('v2_llm_graph.src.agent_graph.VectorMemory') as mock_memory, \
         patch('v2_llm_graph.src.agent_graph.llm') as mock_llm:
        
        # Arrange
        mock_stock.return_value = {"financials": "test_data"}
        mock_macro.return_value = {"macro": "test_data"}
        mock_news.return_value = {"articles": [{"content": "test news"}]}
        
        mock_memory_instance = MagicMock()
        mock_memory_instance.query_memory.return_value = ["Past analysis"]
        mock_memory_instance.add_analysis.return_value = None
        mock_memory.return_value = mock_memory_instance
        
        mock_llm_response = MagicMock()
        mock_llm_response.text = "Test response"
        mock_llm.generate_content.return_value = mock_llm_response
        
        initial_state = AgentState(
            company_name="Integration Test Corp",
            company_ticker="ITC",
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
        
        # Act
        final_state = app.invoke(initial_state)
        
        # Assert
        assert final_state is not None
        assert "final_report" in final_state
        assert final_state["revision_count"] > 0

@pytest.mark.integration
def test_workflow_error_recovery():
    """
    Test workflow's ability to handle and recover from errors.
    """
    with patch('v2_llm_graph.src.agent_graph.get_stock_fundamentals') as mock_stock, \
         patch('v2_llm_graph.src.agent_graph.get_macro_economic_data') as mock_macro, \
         patch('v2_llm_graph.src.agent_graph.get_company_news') as mock_news:
        
        # Arrange - simulate intermittent API failure
        mock_stock.side_effect = [Exception("API Error"), {"financials": "retry_success"}]
        mock_macro.return_value = {"macro": "test_data"}
        mock_news.return_value = {"articles": []}
        
        initial_state = AgentState(
            company_name="Recovery Test Corp",
            company_ticker="RTC",
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
        
        # Act
        result = gather_data_node(initial_state)
        
        # Assert
        assert "financial_data" in result
        assert "error" in result["financial_data"]