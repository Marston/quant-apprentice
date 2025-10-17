import os
import json
import re
import google.generativeai as genai


def analyze_article_chain(article_content: str, llm: genai.GenerativeModel) -> dict:
    """
    Analyzes a news article using a single, structured prompt to Gemini.
    This function performs sentiment analysis, extracts key takeaways, and summarizes the article.

    Args:
        article_content: The full text content of the news article.
        llm: The initialized Gemini GenerativeModel instance.

    Returns:
        A dictionary containing the structured analysis or an error message.
    """
    print("--- [Workflow Action]: Starting News Analysis Chain... ---")

    # This master prompt instructs the LLM to perform all tasks in one go
    # and return a structured JSON object.
    prompt = f"""
    As a financial analyst, analyze the following news article. Your task is to perform three steps:
    1.  Determine the overall sentiment (Positive, Negative, or Neutral).
    2.  Extract the 3 most important, bullet-point key takeaways from the article.
    3.  Provide a concise 2-sentence summary of the article's core message.

    The article must be analyzed from the perspective of an investor in the company mentioned.

    Here is the article content:
    ---
    {article_content}
    ---

    Please provide the output in a single, valid JSON object with the following keys: "sentiment", "key_takeaways", "summary".
    Example format:
    {{
      "sentiment": "Positive",
      "key_takeaways": [
        "Takeaway 1...",
        "Takeaway 2...",
        "Takeaway 3..."
      ],
      "summary": "Summary sentence 1. Summary sentence 2."
    }}
    """

    try:
        response = llm.generate_content(prompt)
        
        # Clean the response to ensure it's valid JSON
        # Gemini sometimes wraps its JSON response in ```json ... ```
        cleaned_response = re.sub(r"```json\n?|```", "", response.text)
        
        # Parse the JSON string into a Python dictionary
        analysis_result = json.loads(cleaned_response)
        
        print("--- [Workflow Success]: News Analysis Chain completed. ---")
        return analysis_result

    except json.JSONDecodeError:
        error_message = "Failed to decode JSON from the model's response."
        print(f"--- [Workflow Error]: {error_message} ---")
        print(f"--- [Raw Response]: {response.text} ---")
        return {"error": error_message, "raw_response": response.text}
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        print(f"--- [Workflow Error]: {error_message} ---")
        return {"error": error_message}