import os
from typing import TypedDict, List, Annotated
import operator

from dotenv import load_dotenv
import google.generativeai as genai
from langgraph.graph import StateGraph, END

# --- Import all our project's tools and workflows ---
from .tools.financial_data_fetcher import get_stock_fundamentals, get_macro_economic_data
from .tools.news_fetcher import get_company_news
from .tools.sec_filings_fetcher import get_latest_sec_filings
from .workflows.news_analysis_chain import analyze_article_chain
from .workflows.specialist_router import route_and_execute_task
from .workflows.report_evaluator import SYNTHESIS_PROMPT_TEMPLATE, EVALUATOR_PROMPT_TEMPLATE, REFINEMENT_PROMPT_TEMPLATE
# memory using chromadb
from .memory.vector_memory import VectorMemory


# --- 1. Define the Agent's State ---
# This TypedDict defines the structure of the data that flows through the graph.
class AgentState(TypedDict):
    company_name: str
    company_ticker: str
    financial_data: dict
    macro_data: dict
    news_data: dict
    structured_news_analysis: dict
    financial_analysis: str
    news_impact_analysis: str
    market_context_analysis: str
    draft_report: str
    sec_filings_data: dict
    # memory component
    past_analysis: str
    feedback: str
    final_report: str
    revision_count: int
 

# --- Configure the LLM ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
llm = genai.GenerativeModel('gemini-2.5-pro', generation_config={'temperature': 0.2})

# --- 2. Define the Graph Nodes ---
# Each node is a function that takes the state as input and returns a dictionary to update the state.

def sec_filings_node(state: AgentState):
    print("[Node]: Fetching SEC Filings...")
    company_ticker = state['company_ticker']
    sec_data = get_latest_sec_filings(company_ticker, os.getenv("SEC_API_KEY"))
    return {"sec_filings_data": sec_data}


def gather_data_node(state: AgentState):
    print("[Node]: Gathering Data...")
    company_name = state['company_name']
    company_ticker = state['company_ticker']
    
    try:
        financial_data = get_stock_fundamentals(company_ticker)
    except Exception as e:
        print(f"[Error] Failed to fetch stock fundamentals: {str(e)}")
        financial_data = {"error": str(e), "data": {}}
        
    try:
        macro_data = get_macro_economic_data(os.getenv("FRED_API_KEY"))
    except Exception as e:
        print(f"[Error] Failed to fetch macro data: {str(e)}")
        macro_data = {"error": str(e), "data": {}}
        
    try:
        news_data = get_company_news(company_name, os.getenv("NEWS_API_KEY"), num_articles=3)
    except Exception as e:
        print(f"[Error] Failed to fetch news data: {str(e)}")
        news_data = {"error": str(e), "articles": []}
    
    return {
        "financial_data": financial_data,
        "macro_data": macro_data,
        "news_data": news_data
    }
    

def specialist_analysis_node(state: AgentState):
    print("[Node]: Performing Specialist Analysis...")
    news_data = state['news_data']
    financial_data = state['financial_data']
    macro_data = state['macro_data']
    
    # Process news with prompt chaining
    processed_analyses = [analyze_article_chain(article['content'], llm) for article in news_data["articles"]]
    structured_news_analysis = {"news_items": processed_analyses}

    # Route to specialists
    financial_analysis = route_and_execute_task('analyze_financials', financial_data, llm)
    news_impact_analysis = route_and_execute_task('analyze_news_impact', structured_news_analysis, llm)
    market_context_analysis = route_and_execute_task('analyze_market_context', macro_data, llm)
    
    return {
        "structured_news_analysis": structured_news_analysis,
        "financial_analysis": financial_analysis,
        "news_impact_analysis": news_impact_analysis,
        "market_context_analysis": market_context_analysis
    }


def synthesize_report_node(state: AgentState):
    print("[Node]: Synthesizing Draft Report...")
    try:
        prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
            company_name=state['company_name'],
            past_analysis=state['past_analysis'],
            sec_filings_summary=state.get('sec_filings_data', 'Not available'),
            financial_analysis=state['financial_analysis'],
            news_impact_analysis=state['news_impact_analysis'],
            market_context_analysis=state['market_context_analysis']
        )
        draft_report = llm.generate_content(prompt, timeout=30).text
    except Exception as e:
        print(f"[Error] LLM synthesis error: {str(e)}")
        draft_report = f"Error generating report: {str(e)}"
    
    revision_count = state.get('revision_count', 0) + 1
    return {"draft_report": draft_report, "revision_count": revision_count}


def evaluate_report_node(state: AgentState):
    print("[Node]: Evaluating Draft Report...")
    prompt = EVALUATOR_PROMPT_TEMPLATE.format(draft_report=state['draft_report'])
    feedback = llm.generate_content(prompt).text
    return {"feedback": feedback}


def refine_report_node(state: AgentState):
    print("[Node]: Refining Final Report...")
    prompt = REFINEMENT_PROMPT_TEMPLATE.format(
        company_name=state['company_name'],
        financial_analysis=state['financial_analysis'],
        news_impact_analysis=state['news_impact_analysis'],
        market_context_analysis=state['market_context_analysis'],
        feedback=state['feedback']
    )
    final_report = llm.generate_content(prompt).text
    return {"final_report": final_report}


def retrieve_from_memory_node(state: AgentState):
    print("--- [Node]: Retrieving from Vector Memory... ---")
    company_name = state['company_name']
    try:
        memory = VectorMemory()
        # Formulate a query to find relevant past analyses
        query = f"What was my past analysis and conclusion for {company_name}?"
        results = memory.query_memory(query, n_results=1)
        
        if results:
            past_analysis = "\n".join(results)
            print(f"--- [Memory]: Found relevant past analysis. ---")
        else:
            past_analysis = "No prior analysis found in memory."
            print(f"--- [Memory]: No relevant past analysis found. ---")
    except Exception as e:
        print(f"[Error] Memory system error: {str(e)}")
        past_analysis = f"Error accessing memory system: {str(e)}"
        
    return {"past_analysis": past_analysis}


def save_to_memory_node(state: AgentState):
    print("--- [Node]: Saving to Vector Memory... ---")
    company_ticker = state['company_ticker']
    # Save the final report if it exists, otherwise save the draft
    report_to_save = state.get('final_report') or state.get('draft_report')
    
    if report_to_save:
        memory = VectorMemory()
        memory.add_analysis(company_ticker, report_to_save)
    
    # This is a final node, so it doesn't need to return anything to the state
    return {}


# --- 3. Define Conditional Edges ---
# This function decides where to go after the evaluation node.
def should_refine_or_end(state: AgentState):
    """
    Uses the LLM to decide whether to refine the report or end the process.
    """
    print("--- [Conditional Edge]: Using LLM to check feedback... ---")
    feedback = state['feedback']
    revision_count = state['revision_count']
    
    if revision_count > 1:
        print("--- [Decision]: Maximum revisions reached. Ending. ---")
        return "end"
    
    # Create a dedicated prompt for the decision
    decision_prompt = f"""
    You are a gatekeeper. Your task is to decide if a report needs revision based on the following feedback.
    If the feedback points out any flaws, weaknesses, or areas for improvement, a revision is required.
    
    Feedback:
    ---
    {feedback}
    ---
    
    Based on the feedback, is a revision required? Answer ONLY with the word "Yes" or "No".
    """
    
    try:
        response = llm.generate_content(decision_prompt)
        decision = response.text.strip().lower()
        
        if "yes" in decision:
            print("--- [LLM Decision]: Feedback requires revision. Refining report. ---")
            return "refine"
        else:
            print("--- [LLM Decision]: Feedback is positive or sufficient. Ending. ---")
            return "end"
            
    except Exception as e:
        print(f"--- [Error]: Could not make a decision. Defaulting to end. Details: {e} ---")
        return "end"
    

# --- 4. Assemble the Graph ---
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("gather_data", gather_data_node)
workflow.add_node("retrieve_from_memory", retrieve_from_memory_node)
workflow.add_node("fetch_sec_filings", sec_filings_node)
workflow.add_node("analyze_specialists", specialist_analysis_node)
workflow.add_node("synthesize_report", synthesize_report_node)
workflow.add_node("evaluate_report", evaluate_report_node)
workflow.add_node("refine_report", refine_report_node)
workflow.add_node("save_to_memory", save_to_memory_node)

# Set entry and standard edges
workflow.set_entry_point("gather_data")
workflow.add_edge("gather_data", "retrieve_from_memory")
workflow.add_edge("retrieve_from_memory", "fetch_sec_filings")
workflow.add_edge("fetch_sec_filings", "analyze_specialists")
workflow.add_edge("analyze_specialists", "synthesize_report")
workflow.add_edge("synthesize_report", "evaluate_report")
workflow.add_edge("refine_report", "save_to_memory")
workflow.add_edge("save_to_memory", END)

# Add conditional edge
workflow.add_conditional_edges(
    "evaluate_report",
    should_refine_or_end,
    {
        "refine": "refine_report",
        "end": "save_to_memory"
    }
)

# Compile the graph into a runnable app
app = workflow.compile()