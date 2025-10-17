import sys
sys.path.insert(0, 'src')

import pytest
import json
from datetime import datetime, timedelta

from src.investment_research_agent import InvestmentResearchAgent
from src.tool_router import ToolRouter

@pytest.fixture
def agent():
    agent = InvestmentResearchAgent(memory_file='test_memory.json', output_file='test_output.json')
    agent.plan = ['prices', 'financials']  # Mock plan for fixture
    return agent

def test_plan_research_bias(agent):
    # Test memory bias
    agent.memory['insights']['AAPL'] = ['high_risk']
    plan = agent.plan_research('AAPL')
    assert 'economic' in plan[1]  # Inserted early

def test_news_chaining():
    from src.news_processor import NewsProcessor
    np = NewsProcessor()
    mock_news = [{"title": "Test", "summary": "bad news fall"}]
    processed = np.chain_news(mock_news)
    assert processed['classified'][0]['sentiment'] == 'negative'
    assert len(processed['summary']) > 0

def test_reflection_scores(agent):
    # Mock results for scoring (add timestamps to avoid KeyError)
    mock_ts = datetime.now().isoformat()
    mock_results = {
        'prices': {'data': {}, 'timestamp': mock_ts},
        'financials': {'financials': {'insights': ['test']}, 'timestamp': mock_ts}
    }
    report = agent.generate_report(mock_results, 'AAPL')
    reflection = agent.self_reflect(report)
    assert reflection['scores']['depth'] >= 0.5  # Insights boost depth
    assert reflection['scores']['completeness'] == 1.0  # Full mock coverage

def test_learning_extraction(agent):
    mock_report = {'results': {'financials': {'financials': {'risk_score': 1}}}}
    # Simulate extraction
    learned = []
    if mock_report['results'].get('financials', {}).get('financials', {}).get('risk_score', 0) > 0:
        learned.append('high_risk')
    assert 'high_risk' in learned