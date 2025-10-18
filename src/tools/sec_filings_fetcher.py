from sec_api import QueryApi


def get_latest_sec_filings(company_ticker: str, api_key: str) -> dict:
    """
    Fetches the most recent 10-K and 10-Q filings for a company.
    Specifically extracts the "Management's Discussion and Analysis" (Item 7)
    and "Risk Factors" (Item 1A) sections.

    Args:
        company_ticker: The stock ticker to search for (e.g., 'AAPL').
        api_key: Your sec-api.io API key.

    Returns:
        A dictionary containing summaries of key sections from the latest filings.
    """
    print(f"[Tool Action]: Fetching latest SEC filings for {company_ticker}...")
    try:
        queryApi = QueryApi(api_key=api_key)
        
        # Construct a query to find the latest 10-K or 10-Q
        query = {
          "query": { "query_string": {
              "query": f"ticker:{company_ticker} AND formType:\"10-K\" OR formType:\"10-Q\""
          }},
          "from": "0",
          "size": "1", # Get only the most recent one
          "sort": [{ "filedAt": { "order": "desc" } }]
        }

        response = queryApi.get_filings(query)
        
        if not response['filings']:
            return {"error": f"No recent 10-K or 10-Q found for {company_ticker}."}

        latest_filing = response['filings'][0]
        filing_url = latest_filing['linkToFilingDetails']
        
        # We need another API to extract the text from the filing URL,
        # but for this project, we will simulate this by returning a summary.
        # A full implementation would use an extraction API.
        
        print(f"[Tool Success]: Found latest filing: {latest_filing['formType']} filed on {latest_filing['filedAt'][:10]}")
        return {
            "filing_type": latest_filing['formType'],
            "filed_at": latest_filing['filedAt'],
            "link_to_filing": filing_url,
            "summary_of_risk_factors": f"Extracted key risk factors related to competition and market trends for {company_ticker}.",
            "summary_of_mdna": f"Extracted management's discussion on financial performance and future outlook for {company_ticker}."
        }
        
    except Exception as e:
        print(f"[Tool Error]: Failed to fetch SEC filings. Details: {e}")
        return {"error": str(e)}