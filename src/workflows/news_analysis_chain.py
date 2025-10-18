import os
import json
import re
import google.generativeai as genai


def analyze_article_chain(article_content: str, llm: genai.GenerativeModel) -> dict:
    """
    Analyzes a news article using a single, structured prompt to Gemini.
    This version includes a Chain-of-Thought reasoning step and a rubric for more accurate financial sentiment.

    Args:
        article_content: The full text content of the news article.
        llm: The initialized Gemini GenerativeModel instance.

    Returns:
        A dictionary containing the structured analysis or an error message.
    """
    print("--- [Workflow Action]: Starting Refined News Analysis Chain... ---")

    # This refined prompt forces a step-by-step financial analysis before concluding.
    prompt = f"""
    You are a skeptical financial analyst. Your task is to analyze the following news article from the perspective of a cautious investor.

    **Analysis Steps:**
    1.  **Reasoning:** In a single sentence, explain the likely financial impact of this news on the company's bottom line, stock price, or market position.
    2.  **Sentiment Classification:** Based *only* on your reasoning, classify the sentiment as 'Positive', 'Negative', or 'Neutral' according to the rubric below.
    3.  **Key Takeaways:** Extract the 3 most important, bullet-point key takeaways.
    4.  **Summary:** Provide a concise 2-sentence summary.

    **Sentiment Rubric:**
    - **Positive**: The news is likely to have a direct, favorable impact on revenue, earnings, or market share. (e.g., beating earnings estimates, successful product launch, major new partnership).
    - **Negative**: The news suggests a direct risk to earnings, operations, or brand reputation. (e.g., regulatory fines, missed earnings, executive scandal, major product recall).
    - **Neutral**: The news is informational but does not have a clear, immediate financial impact. (e.g., minor software updates, lateral executive moves, general industry commentary).

    **Article Content:**
    ---
    {article_content}
    ---

    Provide the output in a single, valid JSON object with the keys: "reasoning", "sentiment", "key_takeaways", "summary".
    """

    try:
        response = llm.generate_content(prompt)
        cleaned_response = re.sub(r"```json\n?|```", "", response.text)
        analysis_result = json.loads(cleaned_response)
        
        print("--- [Workflow Success]: Refined News Analysis completed. ---")
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