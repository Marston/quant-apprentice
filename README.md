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

* **Description**: The first integration of an LLM (Gemini) into the workflow. 
This version replaces the rule-based logic with LLM prompts for tasks like news analysis and report synthesis, 
but still follows a linear, top-to-bottom script.
* **How to Run**: See the `v1_linear_agent.ipynb` notebook inside this directory.

### 📁 `v2_llm_graph/`

* **Description**: The final and most advanced version of the agent, rebuilt as a stateful, cyclical graph.
This version uses LangGraph, incorporates a vector database for semantic memory (RAG), an expanded toolset
(SEC filings), and a robust self-critique loop. **This is the final version for submission.**
* **How to Run**: See the `v2_graph_agent.ipynb` notebook inside this directory.

## 🧪 Testing

The project maintains comprehensive test coverage across all components:

```bash
# Run full test suite with coverage reporting
python -m pytest tests/ --cov=v2_llm_graph --cov-report=term-missing -v

# Run only unit tests (excluding integration tests)
python -m pytest tests/ -v -k "not integration"
```

Current test coverage:

* Overall coverage: 95%
* Core components:
  * Agent Graph: 90%
  * Tools (News, SEC, Financial): 100%
  * Vector Memory: 100%
  * Workflows: 100%

## 🚀 Getting Started (for Final Version 2)

### Platform Support

This project was developed and tested on macOS but should be platform-independent as it uses:

* Python's standard library and cross-platform packages
* Conda for environment management
* SQLite-based vector storage (ChromaDB)
* Standard file paths with `os.path` for compatibility

If you encounter any platform-specific issues, please open an issue on GitHub.

### 1. Set up Environment

It is recommended to use a Conda environment.

```bash
conda env create -f src/environment.yml
conda activate quant-apprentice
```

### 2. Create `.env` File

The agent requires API keys for various data sources. Create a `.env` file in the root directory and  
add the following, replacing `your_key_here` with your actual API keys:

```bash
GOOGLE_API_KEY="your_key_here"
NEWS_API_KEY="your_key_here"
SEC_API_KEY="your_key_here"
FRED_API_KEY="your_key_here"
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Verify Setup

Run the test suite to ensure everything is set up correctly:

```bash
# Run tests with coverage report
python -m pytest tests/ --cov=v2_llm_graph --cov-report=term-missing -v
```

## Project Structure (v2)

```bash
src/v2_llm_graph/
├── v2_graph_agent.ipynb     # Main entry point
├── src/
│   ├── agent_graph.py       # Core agent architecture
│   ├── tools/               # Data gathering tools
│   │   ├── financial_data_fetcher.py
│   │   ├── news_fetcher.py
│   │   └── sec_filings_fetcher.py
│   ├── workflows/           # Analysis chains
│   │   ├── news_analysis_chain.py
│   │   ├── report_evaluator.py
│   │   └── specialist_router.py
│   └── memory/             # Vector storage
│       └── vector_memory.py
└── tests/                  # Comprehensive test suite
    ├── test_v2_tools.py
    ├── test_v2_memory.py
    ├── test_v2_workflows.py
    └── test_v2_agent_graph.py
```

## Error Handling

The system includes comprehensive error handling for:

* API failures and timeouts
* Memory system errors
* LLM interaction issues
* Data processing edge cases

All error cases are covered by integration tests to ensure robust operation.
