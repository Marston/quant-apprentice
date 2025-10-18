# workflows/report_evaluator.py

import google.generativeai as genai

# Agent Prompts for Synthesis and Evaluation 

# --- Agent Prompts for Synthesis and Evaluation ---

SYNTHESIS_PROMPT_TEMPLATE = """
You are a Chief Investment Strategist. Your task is to synthesize the analyses from your specialist teams into a final, coherent investment report.

**PRIOR ANALYSIS FOR CONTEXT (from your memory):**
---
{past_analysis}
---

**LATEST SEC FILING INSIGHTS:**
---
{sec_filings_summary}
---

**CURRENT SPECIALIST REPORTS:**
---

**Quantitative Financial Analysis:**
{financial_analysis}
---

**News Impact Analysis:**
{news_impact_analysis}

---
**Macroeconomic Context:**
{market_context_analysis}
---

Based on these inputs, create a comprehensive investment report for {company_name}. The report must include:
1.  **Executive Summary (2-3 sentences)**: A high-level overview of the findings.
2.  **Key Findings**: A bulleted list combining the most critical points from all three analyses.
3.  **Final Recommendation**: A clear 'Buy', 'Hold', or 'Sell' rating.
4.  **Justification (3 bullet points)**: A clear, data-driven rationale for your recommendation, referencing the specialist reports.
"""

EVALUATOR_PROMPT_TEMPLATE = """
You are a skeptical Risk Manager. Your job is to critique an investment report written by a strategist.
Read the following draft report and provide constructive feedback. Your feedback should identify potential weaknesses, biases, or gaps in the analysis.
Focus on questions like:
- Is the recommendation too optimistic or pessimistic?
- Does the justification strongly support the recommendation?
- Is there a key risk that was overlooked?
- Is the analysis balanced?

Provide your feedback in a concise, 2-4 bullet point list. Be critical but constructive.

**DRAFT REPORT TO EVALUATE:**
---
{draft_report}
---
"""

REFINEMENT_PROMPT_TEMPLATE = """
You are the Chief Investment Strategist. Your initial draft report was reviewed by a Risk Manager.
Your task is to revise your report based on their feedback to create a more robust and balanced final version.

**Original Specialist Reports:**
---
**1. Quantitative Financial Analysis:**
{financial_analysis}
---
**2. News Impact Analysis:**
{news_impact_analysis}
---
**3. Macroeconomic Context:**
{market_context_analysis}
---

**Risk Manager's Feedback:**
---
{feedback}
---

Now, generate the final, refined investment report for {company_name}, incorporating the feedback. The structure (Executive Summary, Key Findings, Recommendation, Justification) must remain the same.
"""

# --- Workflow Function ---

def generate_and_evaluate_report(
    company_name: str, 
    financial_analysis: str, 
    news_impact_analysis: str, 
    market_context_analysis: str, 
    llm: genai.GenerativeModel
) -> dict:
    """
    Orchestrates the generate -> evaluate -> refine workflow.

    Returns:
        A dictionary containing the initial draft, feedback, and the final refined report.
    """
    print("--- [Workflow Action]: Starting Report Generation & Evaluation Loop... ---")
    
    # 1. GENERATE INITIAL DRAFT
    print("--- [Step 1]: Generating initial draft report... ---")
    synthesis_prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
        company_name=company_name,
        financial_analysis=financial_analysis,
        news_impact_analysis=news_impact_analysis,
        market_context_analysis=market_context_analysis
    )
    try:
        draft_report = llm.generate_content(synthesis_prompt).text
    except Exception as e:
        return {"error": f"Failed during initial draft generation: {e}"}

    # 2. EVALUATE DRAFT
    print("--- [Step 2]: Evaluating draft with Risk Manager agent... ---")
    evaluator_prompt = EVALUATOR_PROMPT_TEMPLATE.format(draft_report=draft_report)
    try:
        feedback = llm.generate_content(evaluator_prompt).text
    except Exception as e:
        return {"error": f"Failed during evaluation step: {e}"}

    # 3. REFINE DRAFT BASED ON FEEDBACK
    print("--- [Step 3]: Refining report based on feedback... ---")
    refinement_prompt = REFINEMENT_PROMPT_TEMPLATE.format(
        company_name=company_name,
        financial_analysis=financial_analysis,
        news_impact_analysis=news_impact_analysis,
        market_context_analysis=market_context_analysis,
        feedback=feedback
    )
    try:
        final_report = llm.generate_content(refinement_prompt).text
    except Exception as e:
        return {"error": f"Failed during refinement step: {e}"}

    print("--- [Workflow Success]: Report generation loop complete. ---")
    return {
        "draft_report": draft_report,
        "feedback": feedback,
        "final_report": final_report
    }