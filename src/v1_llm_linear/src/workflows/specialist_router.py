import google.generativeai as genai

# Specialist Analyst Prompts

FINANCIAL_ANALYST_PROMPT = """
As a Quantitative Financial Analyst, your task is to analyze the provided key financial metrics for a company.
Focus on valuation, profitability, and financial health.
Provide a 3-5 bullet point summary of your findings, highlighting strengths and weaknesses.
Do not make a final recommendation. Your analysis must be objective and based solely on the data provided.

**Financial Data:**
{financial_data}
"""

NEWS_ANALYST_PROMPT = """
As an Investment News Analyst, your task is to interpret the provided structured news analysis.
Based on the sentiment, key takeaways, and summary, what is the likely short-term impact on the company's stock price?
Consider the source and content of the news. Provide a 2-3 sentence summary of your impact assessment.

**Structured News Analysis:**
{news_analysis}
"""

MARKET_ANALYST_PROMPT = """
As a Macroeconomic Analyst, your task is to provide market context based on the latest economic indicators.
How might the current economic environment (inflation, interest rates, GDP) affect the broader stock market and the sector this company operates in?
Provide a 2-3 sentence summary of the overall market sentiment based on this data.

**Macroeconomic Data:**
{macro_data}
"""


def route_and_execute_task(task_type: str, data: dict, llm: genai.GenerativeModel) -> str:
    """
    Routes data to the correct specialist analyst based on the task type.

    Args:
        task_type: The type of analysis to perform ('analyze_financials', 'analyze_news_impact', 'analyze_market_context').
        data: The data payload for the analysis.
        llm: The initialized Gemini GenerativeModel instance.

    Returns:
        The text response from the selected specialist analyst.
    """
    
    prompt = ""
    if task_type == 'analyze_financials':
        print(f"--- [Router]: Routing to Financial Analyst... ---")
        prompt = FINANCIAL_ANALYST_PROMPT.format(financial_data=data)
    elif task_type == 'analyze_news_impact':
        print(f"--- [Router]: Routing to News Analyst... ---")
        prompt = NEWS_ANALYST_PROMPT.format(news_analysis=data)
    elif task_type == 'analyze_market_context':
        print(f"--- [Router]: Routing to Market Analyst... ---")
        prompt = MARKET_ANALYST_PROMPT.format(macro_data=data)
    else:
        return "--- [Router Error]: Invalid task type provided. ---"

    try:
        response = llm.generate_content(prompt)
        print(f"--- [Router]: Specialist analysis complete. ---")
        return response.text
    except Exception as e:
        error_message = f"An error occurred during specialist execution: {e}"
        print(f"--- [Router Error]: {error_message} ---")
        return error_message