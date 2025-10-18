Quant Apprentice 📈

Quant Apprentice is an autonomous AI agent for sophisticated, end-to-end financial analysis. This repository showcases the evolution of the agent through three distinct versions, from a simple rule-based system to a complex, self-reflecting agentic workflow powered by Google's Gemini 1.5 Pro.

Project Versions

This repository is organized into three distinct versions to demonstrate the project's development lifecycle.

📁 v0_no_llm/ - Version 0: The Rule-Based Analyst

Description: A foundational version of the agent built with pure Python, without any Large Language Models.

Logic: It follows a hard-coded plan, uses simple rule-based logic for analysis (e.g., keyword searches for sentiment), and demonstrates the basic structure of an automated research agent.

How to Run: See the demo.ipynb notebook inside this directory.

📁 v1_llm_linear/ - Version 1: The LLM-Powered Analyst

Description: The first integration of an LLM (Gemini) into the workflow.

Logic: This version replaces the rule-based logic with LLM prompts for tasks like news analysis and report synthesis. However, it still follows a linear, top-to-bottom script. It introduces the core concepts of Prompt Chaining and Routing.

How to Run: See the v1_linear_agent.ipynb notebook inside this directory.

📁 v2_llm_graph/ - Version 2: The Agentic System (Final Version)

Description: The final and most advanced version of the agent, rebuilt as a stateful, cyclical graph. This is the complete project submission.

Logic: This version uses LangGraph to manage the agent's state and control flow. It incorporates a vector database for semantic memory (RAG), an expanded toolset (SEC filings), and a robust self-critique loop where the agent uses an LLM to decide whether to refine its own work.

How to Run: See the v2_graph_agent.ipynb notebook inside this directory.

Agent Workflow Diagram (Version 2)

This diagram illustrates the flow of data and logic in the final, graph-based agent.

graph TD
    subgraph "Input & Data Gathering (Phase 1)"
        A[Stock Ticker] --> B(Get Financial Data);
        A --> C(Get News Articles);
        A --> D(Get Macro Data);
        C --> E{Process News};
    end

    subgraph "Specialist Analysis (Phase 2)"
        B --> F[Financial Analyst Report];
        E --> G[News Analyst Report];
        D --> H[Market Analyst Report];
    end

    subgraph "Synthesis & Refinement (Phase 3)"
        I((Synthesize)) -- Creates --> J(Draft Report);
        J -- Is sent to --> K((Evaluate));
        K -- Creates --> L(Critic's Feedback);
        J & L -- Are used to --> M((Refine));
        M -- Creates --> N(Final Report);
    end

    subgraph "Output & Learning"
        O[Save to Vector Memory]
    end

    %% --- Connections between phases ---
    F & G & H --> I;
    N --> O;


🛠️ Technology Stack (Version 2)

AI Engine: Google Gemini 1.5 Pro

Agent Framework: LangGraph

Vector Memory: ChromaDB

Core Libraries: google-generativeai, langgraph, chromadb, yfinance, fredapi, newsapi-python, sec-api

Language: Python 3.10+

🚀 Getting Started (Version 2)

1. Clone the Repository

git clone [https://github.com/your-username/quant-apprentice.git](https://github.com/your-username/quant-apprentice.git)
cd quant-apprentice


2. Install Dependencies

pip install -r requirements.txt


3. Set Up API Keys

Copy the .env.example file to a new file named .env and add your secret API keys.

cp .env.example .env
# Now, edit the .env file with your keys


4. Run the Agent

Open the v2_llm_graph/v2_graph_agent.ipynb notebook and run the cells to see the agent perform its full, end-to-end analysis.