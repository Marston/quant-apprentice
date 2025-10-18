# Quant Apprentice 📈

Quant Apprentice is an autonomous AI agent for sophisticated, end-to-end financial analysis.
This repository showcases the evolution of the agent through three distinct versions, from a simple
rule-based system to a complex, self-reflecting agentic workflow powered by Google's Gemini Pro.

## Project Versions

This repository is organized into three distinct, self-contained versions to demonstrate the project's 
development lifecycle. Please see the entry point notebook inside each folder for specific instructions and code.

### 📁 `v0_no_llm/`

* **Description**: A foundational version of the agent built with pure Python, without any Large Language Models. 
It uses hard-coded rules for analysis and demonstrates the basic structure of an automated research agent.
* **How to Run**: See the `demo.ipynb` notebook inside this directory.

### 📁 `v1_llm_linear/`

* **Description**: The first integration of an LLM (Gemini) into the workflow. This version replaces the rule-based logic with LLM prompts for tasks like news analysis and report synthesis, but still follows a linear, top-to-bottom script.
* **How to Run**: See the `v1_linear_agent.ipynb` notebook inside this directory.

### 📁 `v2_llm_graph/`

* **Description**: The final and most advanced version of the agent, rebuilt as a stateful, cyclical graph.
This version uses LangGraph, incorporates a vector database for semantic memory (RAG), an expanded toolset
(SEC filings), and a robust self-critique loop. **This is the final version for submission.**
* **How to Run**: See the `v2_graph_agent.ipynb` notebook inside this directory.

* **How to Run**: See the `v2_graph_agent.ipynb` notebook inside this directory.

---

## 🚀 Getting Started (for Final Version 2)

### 1. Install Dependencies

```bash
    pip install -r requirements.txt
```
