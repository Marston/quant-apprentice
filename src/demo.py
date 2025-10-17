#!/usr/bin/env python
"""
Demo script for InvestmentResearchAgent.
Run: python demo.py
Outputs report to console; in prod, export to Markdown/PDF.
"""
from investment_research_agent import InvestmentResearchAgent


if __name__ == "__main__":
    agent = InvestmentResearchAgent()
    symbol = 'AAPL'
    report = agent.research(symbol)
    print(report)
    # Verify memory: print(json.dumps(agent.memory, indent=2))  # Uncomment for debug