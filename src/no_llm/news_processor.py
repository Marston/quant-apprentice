import json
import re
from datetime import datetime
from typing import List, Dict, Any


class NewsProcessor:
    def __init__(self):
        self.chain_steps = ['ingest', 'preprocess', 'classify', 'extract', 'summarize']
    
    def chain_news(self, raw_news: List[Dict]) -> Dict[str, Any]:
        """Prompt Chaining: Sequential pipeline for news analysis."""
        processed = {'raw': raw_news, 'timestamp': datetime.now().isoformat()}
        
        # Step 1: Ingest (already fetched; just validate)
        processed['ingested'] = len(raw_news)
        
        # Step 2: Preprocess (clean text: remove URLs, lowercase, tokenize stub)
        cleaned = []
        for item in raw_news:
            text = item['summary'] or ''
            cleaned_text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)  # Remove URLs
            cleaned_text = re.sub(r'\W+', ' ', cleaned_text.lower()).strip()  # Normalize
            cleaned.append({'title': item['title'], 'cleaned_summary': cleaned_text[:200]})
        processed['preprocessed'] = cleaned
        
        # Step 3: Classify (simple sentiment: rule-based; positive/negative/neutral)
        classified = []
        for item in cleaned:
            summary = item['cleaned_summary']
            pos_words = len(re.findall(r'\b(good|great|rise|strong|positive)\b', summary))
            neg_words = len(re.findall(r'\b(bad|fall|weak|decline|negative)\b', summary))
            sentiment = 'positive' if pos_words > neg_words else 'negative' if neg_words > pos_words else 'neutral'
            classified.append({**item, 'sentiment': sentiment, 'score': abs(pos_words - neg_words)})
        processed['classified'] = classified
        
        # Step 4: Extract (key entities: companies, dates, numbers stub via regex)
        extracted = []
        for item in classified:
            entities = {
                'companies': re.findall(r'\b(AAPL|Apple|UBS|NASDAQ)\b', item['title'] + ' ' + item['cleaned_summary']),
                'dates': re.findall(r'\b(2025|October|Oct|30)\b', item['title'] + ' ' + item['cleaned_summary']),
                'numbers': re.findall(r'\$\d+(?:\.\d{2})?', item['title'] + ' ' + item['cleaned_summary'])
            }
            extracted.append({**item, 'entities': entities})
        processed['extracted'] = extracted
        
        # Step 5: Summarize (extractive: top 2 by sentiment score, concat)
        top_items = sorted(extracted, key=lambda x: x['score'], reverse=True)[:2]
        summary = ' | '.join([f"{item['title']}: {item['sentiment']} ({item['entities']})" for item in top_items])
        processed['summary'] = summary
        
        return processed