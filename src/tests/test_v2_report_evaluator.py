import pytest
from unittest.mock import patch, MagicMock
from v2_llm_graph.src.workflows.report_evaluator import (
    generate_and_evaluate_report,
    SYNTHESIS_PROMPT_TEMPLATE,
    EVALUATOR_PROMPT_TEMPLATE,
    REFINEMENT_PROMPT_TEMPLATE
)

@pytest.fixture
def mock_llm():
    mock = MagicMock()
    mock.generate_content.side_effect = [
        MagicMock(text="Draft Report Content"),
        MagicMock(text="Feedback Content"),
        MagicMock(text="Final Report Content")
    ]
    return mock

@pytest.fixture
def test_inputs():
    return {
        "company_name": "Test Corp",
        "financial_analysis": "Strong financial performance",
        "news_impact_analysis": "Positive news coverage",
        "market_context_analysis": "Favorable market conditions"
    }

def test_generate_and_evaluate_report_success(mock_llm, test_inputs):
    """Test successful report generation workflow"""
    # Act
    result = generate_and_evaluate_report(
        test_inputs["company_name"],
        test_inputs["financial_analysis"],
        test_inputs["news_impact_analysis"],
        test_inputs["market_context_analysis"],
        mock_llm,
        past_analysis="Test past analysis",
        sec_filings_summary="Test SEC filings"
    )

    # Assert
    assert "error" not in result
    assert mock_llm.generate_content.call_count == 3
    
    # Verify prompt templates were used correctly
    synthesis_call = mock_llm.generate_content.call_args_list[0]
    evaluator_call = mock_llm.generate_content.call_args_list[1]
    refinement_call = mock_llm.generate_content.call_args_list[2]
    
    assert test_inputs["company_name"] in synthesis_call[0][0]
    assert "Draft Report Content" in evaluator_call[0][0]
    assert "Feedback Content" in refinement_call[0][0]

def test_generate_and_evaluate_report_draft_failure(mock_llm, test_inputs):
    """Test handling of failure during draft generation"""
    # Arrange
    mock_llm.generate_content.side_effect = Exception("Draft generation failed")

    # Act
    result = generate_and_evaluate_report(
        test_inputs["company_name"],
        test_inputs["financial_analysis"],
        test_inputs["news_impact_analysis"],
        test_inputs["market_context_analysis"],
        mock_llm,
        past_analysis="Test past analysis",
        sec_filings_summary="Test SEC filings"
    )

    # Assert
    assert "error" in result
    assert "Failed during initial draft generation" in result["error"]
    assert mock_llm.generate_content.call_count == 1

def test_generate_and_evaluate_report_evaluation_failure(mock_llm, test_inputs):
    """Test handling of failure during evaluation"""
    # Arrange
    mock_llm.generate_content.side_effect = [
        MagicMock(text="Draft Report Content"),
        Exception("Evaluation failed"),
    ]

    # Act
    result = generate_and_evaluate_report(
        test_inputs["company_name"],
        test_inputs["financial_analysis"],
        test_inputs["news_impact_analysis"],
        test_inputs["market_context_analysis"],
        mock_llm,
        past_analysis="Test past analysis",
        sec_filings_summary="Test SEC filings"
    )

    # Assert
    assert "error" in result
    assert "Failed during evaluation step" in result["error"]
    assert mock_llm.generate_content.call_count == 2

def test_generate_and_evaluate_report_refinement_failure(mock_llm, test_inputs):
    """Test handling of failure during refinement"""
    # Arrange
    mock_llm.generate_content.side_effect = [
        MagicMock(text="Draft Report Content"),
        MagicMock(text="Feedback Content"),
        Exception("Refinement failed"),
    ]

    # Act
    result = generate_and_evaluate_report(
        test_inputs["company_name"],
        test_inputs["financial_analysis"],
        test_inputs["news_impact_analysis"],
        test_inputs["market_context_analysis"],
        mock_llm,
        past_analysis="Test past analysis",
        sec_filings_summary="Test SEC filings"
    )

    # Assert
    assert "error" in result
    assert "Failed during refinement step" in result["error"]
    assert mock_llm.generate_content.call_count == 3

def test_synthesis_prompt_template_structure():
    """Test the structure of the synthesis prompt template"""
    # Arrange
    test_data = {
        "company_name": "Test Corp",
        "past_analysis": "Previous analysis",
        "sec_filings_summary": "SEC filings data",
        "financial_analysis": "Financial metrics",
        "news_impact_analysis": "News analysis",
        "market_context_analysis": "Market context"
    }

    # Act
    prompt = SYNTHESIS_PROMPT_TEMPLATE.format(**test_data)

    # Assert
    assert "Executive Summary" in prompt
    assert "Key Findings" in prompt
    assert "Final Recommendation" in prompt
    assert "Justification" in prompt
    assert all(value in prompt for value in test_data.values())

def test_evaluator_prompt_template_structure():
    """Test the structure of the evaluator prompt template"""
    # Act
    prompt = EVALUATOR_PROMPT_TEMPLATE.format(draft_report="Test draft")

    # Assert
    assert "skeptical Risk Manager" in prompt
    assert "Test draft" in prompt
    assert "too optimistic or pessimistic" in prompt
    assert "key risk" in prompt

def test_refinement_prompt_template_structure():
    """Test the structure of the refinement prompt template"""
    # Arrange
    test_data = {
        "company_name": "Test Corp",
        "financial_analysis": "Financial data",
        "news_impact_analysis": "News analysis",
        "market_context_analysis": "Market context",
        "feedback": "Risk manager feedback"
    }

    # Act
    prompt = REFINEMENT_PROMPT_TEMPLATE.format(**test_data)

    # Assert
    assert "Chief Investment Strategist" in prompt
    assert "Risk Manager's Feedback" in prompt
    assert all(value in prompt for value in test_data.values())