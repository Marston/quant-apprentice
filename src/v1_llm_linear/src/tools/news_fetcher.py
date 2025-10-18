import os
from newsapi import NewsApiClient

def get_company_news(company_name: str, api_key: str, num_articles: int = 5) -> dict:
    """
    Fetches and processes top news headlines for a given company using the NewsAPI.

    Args:
        company_name: The name of the company to search for (e.g., "NVIDIA").
        api_key: Your NewsAPI.org API key.
        num_articles: The number of articles to return.

    Returns:
        A dictionary containing a list of processed articles or an error message.
    """
    print(f"[Tool Action]: Fetching top {num_articles} news articles for {company_name}...")
    try:
        newsapi = NewsApiClient(api_key=api_key)

        # Fetch top headlines. We use the company name as the query.
        # We search for English articles and sort by relevancy.
        top_headlines = newsapi.get_everything(
            q=company_name,
            language='en',
            sort_by='relevancy',
            page_size=num_articles
        )

        if top_headlines['status'] != 'ok':
            return {"error": "Failed to fetch news from NewsAPI."}

        # Process the articles to extract only the information our agent needs.
        processed_articles = []
        for article in top_headlines['articles']:
            processed_articles.append({
                "source": article['source']['name'],
                "title": article['title'],
                "url": article['url'],
                "publishedAt": article['publishedAt'],
                "content": article.get('content', 'No content available.') # Content can sometimes be null
            })
        
        print(f"[Tool Success]: Successfully fetched {len(processed_articles)} articles.")
        return {"articles": processed_articles}

    except Exception as e:
        error_message = f"An error occurred while fetching news: {e}"
        print(f"[Tool Error]: {error_message}")
        return {"error": error_message}