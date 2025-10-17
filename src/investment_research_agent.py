import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

from tool_router import ToolRouter

class InvestmentResearchAgent:
    def __init__(self, memory_file: str = 'agent_memory.json', output_file: str = 'test_output.json'):
        self.memory_file = memory_file
        self.output_file = output_file
        self.memory = self.load_memory()
        self.tool_router = ToolRouter()
        self.plan = []
    
    def load_memory(self) -> Dict:
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {'insights': {}, 'runs': []}
    
    def save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
        self.memory['runs'].append({'timestamp': datetime.now().isoformat(), 'symbol': 'init'})
    
    def plan_research(self, symbol: str) -> List[str]:
        base_plan = [
            'prices',
            'financials',
            'news',
            'edgar',
            'economic'
        ]
        insights = self.memory['insights'].get(symbol, [])
        if 'high_volatility' in insights:
            base_plan.insert(2, 'volatility_analysis')
        if 'high_risk' in insights:
            base_plan.insert(1, 'economic')  # Prioritize context for risk
        if 'earnings_preview_needed' in insights:
            base_plan = ['financials'] + [s for s in base_plan if s != 'financials']
        self.plan = base_plan
        return self.plan
    
    def execute_plan(self, symbol: str) -> Dict[str, Any]:
        results = {}
        for step in self.plan:
            results[step] = self.tool_router.route(step, symbol)
        return results
    
    def generate_report(self, results: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        report = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'plan': self.plan,
            'results': results,
            'reflection': {},
            'learned_insights': []
        }
        return report
    
    def self_reflect(self, report: Dict[str, Any], criteria: List[str] = ['completeness', 'accuracy', 'depth']) -> Dict:
        scores = {}
        ts = datetime.fromisoformat(report['timestamp'])
        plan = report.get('plan', [])
        # Completeness: % plan steps with data (no errors); guard empty plan
        if len(plan) == 0:
            scores['completeness'] = 0.0
        else:
            covered = sum(1 for step in plan if 'error' not in report['results'].get(step, {}))
            scores['completeness'] = covered / len(plan)
        # Depth: Insights len + news summary/sentiments; scaled for min 1 insight=0.5
        insight_len = len(report['results'].get('financials', {}).get('financials', {}).get('insights', []))
        news_classified = report['results'].get('news', {}).get('news', {}).get('classified', [])
        news_sentiments = len(set(item['sentiment'] for item in news_classified)) if news_classified else 0
        scores['depth'] = min(1.0, (insight_len + news_sentiments) / 2.0)  # Scaled: 1 insight=0.5, 2=1.0
        # Accuracy: Freshness (<7 days) + no errors; guard missing timestamp
        fresh = 0
        if len(plan) > 0:
            fresh_steps = 0
            total_steps = 0
            for step in plan:
                step_data = report['results'].get(step, {})
                if 'timestamp' in step_data:
                    try:
                        step_ts = datetime.fromisoformat(step_data['timestamp'])
                        if (ts - step_ts).days < 7:
                            fresh_steps += 1
                    except ValueError:
                        pass  # Invalid timestamp: skip
                total_steps += 1
            fresh = fresh_steps / total_steps if total_steps > 0 else 0
        error_free = sum(1 for step in plan if 'error' not in report['results'].get(step, {})) / len(plan) if len(plan) > 0 else 0
        scores['accuracy'] = (fresh + error_free) / 2
        avg_score = sum(scores.values()) / len(scores)
        feedback = f"Avg {avg_score:.2f}: {'Excellent' if avg_score >= 0.9 else 'Good' if avg_score >= 0.75 else 'Refine: Boost depth with more insights'}"
        report['reflection'] = {'scores': scores, 'feedback': feedback, 'avg_score': avg_score}
        return report['reflection']
    
    def research(self, symbol: str, max_refines: int = 2) -> Dict[str, Any]:
        iteration = 0
        report = self.generate_report({}, symbol)
        while iteration <= max_refines:
            self.plan_research(symbol)
            results = self.execute_plan(symbol)
            report = self.generate_report(results, symbol)
            reflection = self.self_reflect(report)
            if reflection['avg_score'] >= 0.75:
                break
            low_crit = min(reflection['scores'], key=reflection['scores'].get)
            low_step = 'financials' if low_crit == 'depth' else 'news'
            report['results'][low_step] = self.tool_router.route(low_step, symbol)
            iteration += 1
            report['refinement'] = f"Refined {low_step} for {low_crit} (iter {iteration})"
        # Learning: Extract & store insights
        learned = []
        if report['results'].get('financials', {}).get('financials', {}).get('risk_score', 0) > 0:
            learned.append('high_risk')
        neg_sent = sum(1 for item in report['results'].get('news', {}).get('news', {}).get('classified', []) if item['sentiment'] == 'negative')
        news_count = len(report['results'].get('news', {}).get('news', {}).get('classified', []))
        if news_count > 0 and neg_sent / news_count > 0.5:
            learned.append('negative_sentiment_bias')
        report['learned_insights'] = learned
        self.memory['insights'][symbol] = self.memory['insights'].get(symbol, []) + learned + ['analyzed on ' + datetime.now().isoformat()]
        if 'earnings_preview_needed' not in self.memory['insights'].get(symbol, []):
            self.memory['insights'][symbol].append('earnings_preview_needed')  # Flag for future
        self.save_memory()
        # Markdown export
        md_report = f"# Research Report: {report['symbol']}\n\n"
        md_report += f"**Timestamp**: {report['timestamp']}\n\n"
        md_report += f"**Plan**: {', '.join(report['plan'])}\n\n"
        for key, data in report['results'].items():
            md_report += f"## {key.upper()}\n{json.dumps(data, indent=2)[:200]}...\n\n"
        md_report += f"**Reflection**: {report['reflection']['feedback']} (Avg: {report['reflection']['avg_score']:.2f})\n"
        md_report += f"**Learned**: {report['learned_insights']}\n"
        with open(f"{symbol}_report.md", 'w') as md:
            md.write(md_report)
        with open(self.output_file, 'w') as f:
            json.dump(report, f, indent=2)
        return report