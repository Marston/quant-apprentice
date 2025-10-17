import json
from investment_research_agent import InvestmentResearchAgent

def run_multi_test():
    agent = InvestmentResearchAgent()
    symbols = ['AAPL', 'TSLA']
    reports = {}
    for symbol in symbols:
        report = agent.research(symbol)
        reports[symbol] = report
        # Assert E2E: Plan len==5+, avg_score>=0.75, learned_insights present
        assert len(report['plan']) >= 5
        assert report['reflection']['avg_score'] >= 0.75
        print(f"{symbol} test passed: Score {report['reflection']['avg_score']:.2f}, Insights: {report['learned_insights']}")
    # Multi-run learning: Re-run AAPL, check bias from TSLA? (cross-symbol stub)
    return reports

if __name__ == "__main__":
    reports = run_multi_test()
    print(json.dumps(reports, indent=2)[:500] + "...")  # Truncate preview
else:
    reports = run_multi_test()
    print(json.dumps(reports, indent=2)[:500] + "...") 